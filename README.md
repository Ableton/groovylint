# Groovylint

This repository provides a way to run [CodeNarc][codenarc-home] checks from a docker
image. CodeNarc analyzes Groovy code for defects, bad practices, inconsistencies, style
issues and more.

## Usage

### Running with Python

To use `groovylint` as a standalone Python script, you should first clone the repository
somewhere on your hard drive. Next, run the `fetch_jars.py` script to fetch CodeNarc's JAR
files:

```bash
$ ./fetch_jars.py --codenarc 1.2.1 --gmetrics 1.0 --slf4j 1.7.25 --output-dir ./resources
```

The version numbers used by `groovylint`'s Docker container can be found in the
`Dockerfile`. After this is finished, you can use `groovylint` from any directory using
Python 3.6 or greater:

```bash
$ /path/to/groovylint/run_codenarc.py --resources /path/to/groovylint/resources \
  --codenarc 1.2.1 --gmetrics 1.0 --slf4j 1.7.25 \
  -- -includes="./Jenkinsfile,**/*.groovy,**/*.gradle"
```

### Running as a Docker application

```bash
$ docker run --rm -v `pwd`:/ws -u `id -u`:`id -g` abletonag/groovylint \
  python3 /opt/run_codenarc.py -- -includes='foo/bar.groovy,src/**/*.groovy'
```

By default this docker image will run CodeNarc checks on `/ws` directory, so this command
mounts the current working directory to that location, and then runs CodeNarc checks on
the files, and exits when finished. Since the default user is `groovy`, it is recommended
that you run the image with your own user ID to avoid permission issues.

The above example would check the file `foo/bar.groovy`, and all Groovy files in the `src`
directory tree.

### Running in a Docker container

```bash
$ docker run --rm -v `pwd`:/ws -u `id -u`:`id -g` --entrypoint=/bin/sh \
  -i -t abletonag/groovylint
```

This command will run the CodeNarc image and override the entry point. You can then run
`codenarc` inside the container as a regular program.

### Specifying the ruleset

As described in the [CodeNarc documentation][codenarc-rules], you can specify your own
ruleset file. The file's location must be relative to your workspace, and can be given in
the command line arguments with the `-rulesetfile` flag:

```bash
$ docker run --rm -v `pwd`:/ws -u `id -u`:`id -g` abletonag/groovylint \
  python3 /opt/run_codenarc.py -- -includes='*.groovy' -rulesetfiles=file:myrules.groovy
```

### Using a codenarc.properties file

As described in the [CodeNarc documentation][codenarc-properties], you can
configure a ruleset with `*.properties` files. Property files must be available
on the Groovy classpath. The Groovy classpath of the docker image is set to
`/opt` in the docker image, so you must mount the properties file there:

```bash
$ docker run --rm -v `pwd`:/ws -v `pwd`/codnearc.properties:/opt/codenarc.properties \
-u `id -u`:`id -g` abletonag/groovylint python3 /opt/run_codenarc.py \
-- -includes='*.groovy' -rulesetfiles=file:myrules.groovy
```

### Usage in a Jenkinsfile

To assist in linting on Jenkins, `groovylint` provides a pipeline library and global
singleton. To use `groovylint` in this manner, you'll need to add it to your [Jenkins
master configuration][jenkins-lib-config]. Any `Jenkinsfile` which is using this library
should also use the version tag, like so:

```groovy
// Example Jenkinsfile using a scripted pipeline
@Library('groovylint@x.y.z') _

node('linux') {
  stage('Lint') {
    groovylint.check('./Jenkinsfile,**/*.groovy')
  }
}
```

Tags are available for all `major.minor.patch` versions, and branches with `major.minor`
versions are updated whenever a new patch version is released. Jenkins exposes the library
version in the environment variables, and the library will use that version to find the
corresponding Docker image for that release.

## Making releases

In order to ensure that the library is using a compatible version of the Docker image, a
file named `VERSION` exists in the top-level directory of this project. To make a release,
this file should be updated accordingly and the commit merged to the `master` branch.

Once on `master`, a new Docker image will be published by Ableton's CI service, which will
also push a corresponding git tag to the origin and update the respective `major.minor`
branch.

## Maintainers

This project is maintained by the following GitHub users:

- [@ala-ableton](https://github.com/ala-ableton)
- [@mst-ableton](https://github.com/mst-ableton)
- [@nre-ableton](https://github.com/nre-ableton)


[codenarc-home]: https://codenarc.github.io/CodeNarc/
[codenarc-rules]: https://codenarc.github.io/CodeNarc/codenarc-rule-index.html
[codenarc-properties]: https://codenarc.github.io/CodeNarc/codenarc-configuring-rules.html#configuring-rules-using-a-properties-file
[jenkins-lib-config]: https://jenkins.io/doc/book/pipeline/shared-libraries/#using-libraries
