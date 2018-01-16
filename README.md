# Groovylint

This repository provides a way to run [CodeNarc](codenarc-home) checks from a docker
image. CodeNarc analyzes Groovy code for defects, bad practices, inconsistencies, style
issues and more.

# Usage

## Running as an application

```
docker run --rm -v `pwd`:/ws -u `id -u`:`id -g` abletonag/groovylint \
  python3 /opt/run_codenarc.py -includes='foo/bar.groovy,src/**/*.groovy'
```

By default this docker image will run CodeNarc checks on `/ws` directory, so this command
mounts the current working directory to that location, and then runs CodeNarc checks on
the files, and exits when finished. Since the default user is `groovy`, it is recommended
that you run the image with your own user ID to avoid permission issues.

The above example would check the file `foo/bar.groovy`, and all Groovy files in the `src`
directory tree.

## Running in a container

```
docker run --rm -v `pwd`:/ws -u `id -u`:`id -g` --entrypoint=/bin/bash \
  -i -t abletonag/groovylint
```

This command will run the CodeNarc image and override the entry point. You can then run
`codenarc` inside the container as a regular program.

## Specifying the ruleset

As described in the [CodeNarc documentation](codenarc-rules), you can specify your own
ruleset file. The file's location must be relative to your workspace, and can be given in
the command line arguments with the `-rulesetfile` flag:

```
docker run --rm -v `pwd`:/ws -u `id -u`:`id -g` abletonag/groovylint \
  python3 /opt/run_codenarc.py -includes='Jenkinsfile' -rulesetfiles=file:myrules.groovy
```

## Usage in a Jenkinsfile

Any `Jenkinsfile` which is using this library should also use the version tag, like so:

```groovy
@Library('codenarc@x.y.z') _
```

Jenkins exposes the library version in the environment variables, and the library will use
that version to find the corresponding Docker image for that release.

# Making releases

In order to ensure that the library is using a compatible version of the Docker image, a
file named `VERSION` exists in the top-level directory of this project. To make a release,
this file should be updated accordingly and the commit merged to the `master` branch.

Once on `master`, a new Docker image will be published by CI. A corresponding git tag
should then be pushed to the origin.


[codenarc-home]: http://codenarc.sourceforge.net
[codenarc-rules]: http://codenarc.sourceforge.net/codenarc-configuring-rules.html
