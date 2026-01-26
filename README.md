# Groovylint

This repository provides a way to run [CodeNarc][codenarc-home] checks from a docker
image. CodeNarc analyzes Groovy code for defects, bad practices, inconsistencies, style
issues and more.

## Usage

`groovylint` is published as a Docker container [on Docker Hub][docker-hub-home]. To
run `groovylint` from the container, that would look something like this:

```bash
$ docker run --rm -u `id -u`:`id -g` -v $PWD:/ws abletonag/groovylint
```

By default, the Docker image will run CodeNarc checks on the `/ws` directory, so
this command uses a volume mapping from the current working directory to that
location.

An include pattern can be passed as the first argument, otherwise a default pattern (see
`entrypoint.sh`).

### On Apple Silicon

Configure the Virtual Machine Options in Docker Desktop to use the Apple Virtualization
Framework, instead of Docker VMM. Otherwise the container might hang indefinitely.

### Usage in a Jenkinsfile

To assist in linting on Jenkins, `groovylint` provides a pipeline library and global
singleton. To use `groovylint` in this manner, you'll need to add it to your [Jenkins
controller configuration][jenkins-lib-config]. Any `Jenkinsfile` which is using this
library should also use the version tag, like so:

```groovy
// Example Jenkinsfile using a scripted pipeline
@Library('groovylint@x.y.z') _

node('linux') {
  stage('Lint') {
    groovylint.check()
  }
}
```

## Making releases

Once on `main`, a new Docker image will be published by Ableton's CI service, which will
also push a corresponding git tag to the origin and update the respective `major.minor`
branch.

## Maintainers

This project is maintained by the following GitHub users:

- [@ala-ableton](https://github.com/ala-ableton)
- [@nre-ableton](https://github.com/nre-ableton)
- [@anz-ableton](https://github.com/anz-ableton)


[codenarc-home]: https://codenarc.github.io/CodeNarc/
[docker-hub-home]: https://hub.docker.com/r/abletonag/groovylint
[jenkins-lib-config]: https://jenkins.io/doc/book/pipeline/shared-libraries/#using-libraries
