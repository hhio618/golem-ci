# golem-deci
Decentralized CI pipline on top of Golem.network.
[![Golem CI](assets/cover.png)](https://github.com/hhio618/golem-ci "Golem CI")


## Example
```sh
$ cd example/hello_world
$ export YAGNA_APPKEY=<your-key>
$ golem_ci up .
Using context directory: golem-ci/example/hello_world
....
```
### How to install the CLI
Run the following command to install the CLI:
```console
pip install golem-ci
```  
Check installed version:
```console
golem_ci --version
```

## Build using docker
```sh
$ docker build -t golem-ci:latest
```

## TODO
Add ipfs support.  
Add frontend.
## Credits
Kaniko project.  
