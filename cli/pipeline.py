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
    def __init__(self, spec, tar_fname):
        """ Creates a new pipeline on top of Golem.network
            params:
                spec: yaml spec file
                tar_fname: tar file to be sent to golem vm.
                pipeline_mode: the excutation mode of pipeline, could be one of PipelineMode.QUEUE|PipelineMode.PARALLEL
        """
        self.spec = spec
        self.tar_fname = tar_fname
        self.step = 0
        self.state = {step['name']:{"state": StepState.PENDING, "log": None} for step in self.spec['steps']}
        # Pipeline mode defaults to PipelineMode.QUEUE.
        self.pipeline_mode = spec.get("mode", PipelineMode.QUEUE)
    
    def get_state():
        """ return the current state of the pipeline """
        return self.state

    def start(self):
        """ Run through steps in parallel or one by one based on the pipeline_mode param. """
        steps = self.spec['steps']
        if self.pipeline_mode == PipelineMode.QUEUE:
            logger.info("start excuting steps in queue mode")
            # first step.
            self.execute([steps[0]])
            while True:
                print(steps[self.step]['name'])
                if self.state[steps[self.step]['name']] in [StepState.SUCCESS, StepState.ERROR]:
                    # step up
                    self.step += 1
                    logger.info(f"executing next step: {steps[self.step]}")
                    self.execute([steps[self.step]])
                else:
                    logger.info(f"waiting for step to be completed: {steps[self.step]}")
                time.sleep(30)
        elif self.pipeline_mode == PipelineMode.PARALLEL:
            logger.info("start excuting steps in parallel mode")
            self.execute(steps)


    def post_progress(self, step_name):
        """ post pipeline progress """
        log_fname = self.state[step_name]["log"]
        with open(log_fname, "r") as f:
            lines = f.readlines()
            for line in lines:
                log.info(line)
             

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



    async def run_step(self, step, timeout=timedelta(minutes=10), budget=100, subnet_tag="community.3" ):
        print(step)
        package = await vm.repo(
            image_hash=step["image"],
            min_mem_gib=1,
            min_storage_gib=5.0,
        )
        async def worker(ctx: WorkContext, tasks):
            async for task in tasks:
                step_name = step['name']
                commands = step['commands']
                envs = step['environment']

                print(f"\033[36;1mSending the context tar file\033[0m")
                ctx.send_file(tar_fname, "/golem/work/context.tar")
                # TODO: set envs.
                logs = []
                for idx, command in enumerate(commands):
                    print(f"\033[36;1mRunning {command}\033[0m")
                    ctx.run(f"bash -c \"{command}\" > /golem/output/cmd.log 2>&1")
                    log_fname = get_temp_log_file(step_name)
                    ctx.download_file(f"/golem/output/cmd_{idx}.log", log_fname)
                print(f"\033[36;1mNo more commands to run!\033[0m")
                try:
                    yield ctx.commit(timeout=timedelta(minutes=30))
                    task.accept_result(result=log_fname)
                except BatchTimeoutError:
                    print(
                        f"{utils.TEXT_COLOR_RED}"
                        f"Task timed out: {task}, time: {task.running_time}"
                        f"{utils.TEXT_COLOR_DEFAULT}"
                    )
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
                self.state[step_name]["log"] = task.output
                self.update_progress(step_name)
