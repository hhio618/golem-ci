#!/usr/bin/env python3
import argparse
import asyncio
import subprocess
import os
import pathlib
import sys
import argparse
import time
from typing import List

import yapapi
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm
from yapapi import Executor, Task, WorkContext
from yapapi.rest.activity import BatchTimeoutError
from datetime import timedelta
from .utils import get_temp_log_file
import logging

logger = logging.getLogger('pipeline')


class StepState:
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class PipelineMode:
    QUEUE = "queue"
    PARALLEL = "parallel"

class Pipeline:
    def __init__(self, spec, tar_fname, verbose=False):
        """ Creates a new pipeline on top of Golem.network
            params:
                spec: yaml spec file
                tar_fname: tar file to be sent to golem vm.
                pipeline_mode: the excutation mode of pipeline, could be one of PipelineMode.QUEUE|PipelineMode.PARALLEL
        """
        self.verbose = verbose
        self.spec = spec
        self.tar_fname = tar_fname
        self.step = 0
        self.state = {step['name']:{"state": StepState.PENDING, "log": None} for step in self.spec['steps']}
        # Pipeline mode defaults to PipelineMode.QUEUE.
        self.pipeline_mode = spec.get("mode", PipelineMode.QUEUE)
    
    def get_state(self):
        """ return the current state of the pipeline """
        return self.state

    def start(self):
        """ Run through steps in parallel or one by one based on the pipeline_mode param. """
        steps = self.spec['steps']
        if self.pipeline_mode == PipelineMode.QUEUE:
            print("start excuting steps in queue mode")
            # first step.
            self.execute([steps[0]])
            while True:
                if self.state[steps[self.step]['name']]['state'] in [StepState.SUCCESS, StepState.ERROR]:
                    if self.step == len(steps)-1:
                        print("all steps have been completed!")
                        return
                    # step up
                    self.step += 1
                    print(f"executing next step: {steps[self.step]}")
                    self.execute([steps[self.step]])
                else:
                    print(f"waiting for step to be completed: {steps[self.step]}")
                time.sleep(30)
        elif self.pipeline_mode == PipelineMode.PARALLEL:
            print("start excuting steps in parallel mode")
            self.execute(steps)


    def post_progress(self, step_name):
        """ post pipeline progress """
        print(f"Step {step_name} completed!")
        log_fname = self.state[step_name]["log"]
        with open(log_fname, "r") as f:
            with open("golem.log", "a") as logf:
                step_log = f.read()
                logf.write(f"#################### Step {step_name} #####################\n" 
                           f"{step_log}\n" 
                           f"##########################################################")
                if self.verbose:
                    print(step_log)
             

    def execute(self, steps: List):
        """ executes a list of steps. """
        enable_default_logger()
        loop = asyncio.get_event_loop()
        for step in steps:
            task = loop.create_task(self.run_step(step))
            try:
                asyncio.get_event_loop().run_until_complete(task)
            except (Exception, KeyboardInterrupt) as e:
                logger.error(e)
                task.cancel()
                asyncio.get_event_loop().run_until_complete(task)



    async def run_step(self, step, timeout=timedelta(minutes=10), budget=10, subnet_tag="community.3" ):
        package = await vm.repo(
            image_hash=step["image"],
            min_mem_gib=1,
            min_storage_gib=5.0,
        )
        async def worker(ctx: WorkContext, tasks):
            async for task in tasks:
                step_name = step['name']
                commands = step['commands']
                # prepair envs in string form of: "k1=v1 k2=v2 ... kn=vn "
                envs = step.get('environment')
                print(f"\033[36;1mSending the context zip file: {self.tar_fname}\033[0m")
                ctx.send_file(self.tar_fname , "/golem/resource/context.zip")
                # extracting tar file.
                print(f"\033[36;1mExtracting the zip file: {self.tar_fname}\033[0m")
                ctx.run("/bin/sh", "-c", "unzip /golem/resource/context.zip")
                # run all commands one by one
                for command in commands:
                    print(f"\033[36;1mRunning {command}\033[0m")
                    # set envs.
                    ctx.run("/bin/sh", "-c", f"{command} >> /golem/output/cmd.log 2>&1", env=envs)
                log_fname = get_temp_log_file(step_name)
                ctx.download_file(f"/golem/output/cmd.log", log_fname)
                try:
                    yield ctx.commit(timeout=timedelta(minutes=30))
                    task.accept_result(result=log_fname)
                except BatchTimeoutError:
                    print(f"Task timed out: {task}, time: {task.running_time}")
                    raise
            ctx.log("no more task to run")

        # By passing `event_emitter=log_summary()` we enable summary logging.
        # See the documentation of the `yapapi.log` module on how to set
        # the level of detail and format of the logged information.
        async with Executor(
            package=package,
            max_workers=1,
            budget=budget,
            timeout=timeout,
            subnet_tag=subnet_tag,
            event_consumer=log_summary(log_event_repr),
        ) as executer:
            async for task in executer.submit(worker, [Task(data=step)]):
                print(f"\033[36;1mStep completed: {task}\033[0m")
                # grab the logs
                self.state[step['name']]['log'] = task.result
                # notify about this task!
                self.state[step['name']]['state'] = StepState.SUCCESS
                self.post_progress(step['name'])
