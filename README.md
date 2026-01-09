# Groovylint

This repository provides a way to run [CodeNarc][codenarc-home] checks from a docker
image. CodeNarc analyzes Groovy code for defects, bad practices, inconsistencies, style
issues and more.

Groovylint is a Maven project that builds a self-contained, so called fat JAR, for
CodeNarc. The self-contained JAR also includes a custom [ruleset][codenarc-rules].

Note that Groovylint used to have been a Python script in the past, until commit
`ec26609`.

## Build

All you need to build the self-contained JAR is an OpenJDK 21+ distribution. To build
everything run the following command from the root of the repository:

```sh
./gradlew clean fatJar
```

- pass `-PcodeNarcVersion=<version>` to build against a different CodeNarc release
- pass `-PgroovyVersion=<version>` to build with a different Groovy interpreter

Use Docker if you don't have a JDK available:

```sh
docker run -v $PWD:/project --workdir /project --rm -it gradle:jdk21-ubi ./gradlew clean fatJar
```

The compiled, self-contained JAR can then be found at
`build/libs/groovylint-*.jar`.

## Run Groovylint

Below is a simple usage example:

```sh
java -jar /path/to/groovylint-fatjar.jar -rulesetfiles=ruleset.groovy -sourcefiles=Jenkinsfile
```

## Docker

A Docker container that contains all the self-contained JARs can be built by running:

```sh
./gradlew docker
```

To use a different image tag pass `-PdockerImageTag=<my-tag>`.

[codenarc-home]: https://codenarc.github.io/CodeNarc/
[codenarc-rules]: https://codenarc.github.io/CodeNarc/codenarc-rule-index.html
