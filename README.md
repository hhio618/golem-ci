
# Golem CI
Decentralized Task pipline on top of Golem.network.
[![Golem CI](assets/cover.png)](https://github.com/hhio618/golem-ci "Golem CI")

## Demo video
[![Golem ci on Golem network](https://img.youtube.com/vi/WNj7LTVS2AI/0.jpg)](https://youtu.be/WNj7LTVS2AI "Golem ci")


## Features
+ Easy way to submit tasks to Golem.network.
+ Collect task logs.
+ Run steps in queue or parallel mode

## Quickstart
### Install yagna
```$ sh curl -sSf https://join.golem.network/as-requestor | bash -```
### Install the cli
Run the following command to install the CLI:
```console
pip install golem-ci
```  
Check installed version:
```console
golem_ci --version
```
### Run yagna daemon
```sh
$ yagna service run
```

### Run the Hello world example 
```sh
$ cd example/hello_world
$ export YAGNA_APPKEY=<your-key> 
$ # or
$ golem_ci set-api-key <your-key> 
$ # then
$ golem_ci up .
Using context directory: hello_world
....
```
## Specification file example
```yaml
kind: pipeline
type: golem
name: hello-world
mode: queue

steps:
- name: echo
  image: 69b8f1cde4b8cf6d2ba6df3d29b4c1ac57beb16aef88e43871726cc6
  commands:
  - python hello.py
  
- name: env-test
  image: 69b8f1cde4b8cf6d2ba6df3d29b4c1ac57beb16aef88e43871726cc6
  commands:
  - python env.py
  environment:
    GOLEM_TEST1: test
    GOLEM_TEST2: 123456
```
See [example](example) for more info.  
To create your own golem image see [Convert a Docker image into a Golem image](https://handbook.golem.network/requestor-tutorials/convert-a-docker-image-into-a-golem-image) 

## Build using docker
```sh
$ docker build -t golem-ci:latest
```
