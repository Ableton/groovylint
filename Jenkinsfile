/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */

library(identifier: 'ableton-utils@0.22', changelog: false)
library(identifier: 'python-utils@0.12', changelog: false)
// Get groovylint library from current commit so it can test itself in this Jenkinsfile
library "groovylint@${params.JENKINS_COMMIT}"


devToolsProject.run(
  setup: { data ->
    data['venv'] = virtualenv.createWithPyenv(readFile('.python-version'))
    data.venv.run('pip install -r requirements-dev.txt')

    data['groovy3Version'] = '3.0.10'
    data['groovy4Version'] = '4.0.2'

    [data.groovy3Version, data.groovy4Version].each { groovyVersion ->
      String groovyZip = "apache-groovy-binary-${groovyVersion}.zip"
      String mirrorHost = 'groovy.jfrog.io/artifactory/dist-release-local/groovy-zips'
      sh "curl -o ${groovyZip} https://${mirrorHost}/${groovyZip}"
      unzip(zipFile: groovyZip)
    }
  },
  build: { data ->
    String gitHash = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    data['image'] = docker.build("abletonag/groovylint:${gitHash}")
  },
  test: { data ->
    parallel(failFast: false,
      black: { data.venv.run('black --check .') },
      flake8: { data.venv.run('flake8 -v') },
      groovydoc: { data['docs'] = groovydoc.generate() },
      'groovylint docker': {
        // Use the Docker image created in the Build stage above. This ensures that the
        // we are checking our own Groovy code with the same library and image which would
        // be published to production.
        groovylint.check(
          includesPattern: './Jenkinsfile,**/*.groovy',
          groovylintImage: data['image'],
        )
      },
      'groovylint native': {
        // Run groovylint using the system Python. This is not a recommended use-case for
        // Jenkins CI installations, but is often more useful for developers running
        // groovylint locally.
        sh "python3 run_codenarc.py --resources ${env.WORKSPACE}/resources" +
          " --groovy-home ${pwd()}/groovy-${data.groovy3Version}" +
          ' -- -includes="./Jenkinsfile,**/*.groovy,**/*.gradle"'
        sh "python3 run_codenarc.py --resources ${env.WORKSPACE}/resources" +
          " --groovy-home ${pwd()}/groovy-${data.groovy4Version} --groovy4" +
          ' -- -includes="./Jenkinsfile,**/*.groovy,**/*.gradle"'
      },
      hadolint: {
        docker.image('hadolint/hadolint:v2.9.3-debian').inside {
          sh 'hadolint Dockerfile'
        }
      },
      pydocstyle: { data.venv.run('pydocstyle -v') },
      pylint: { data.venv.run('pylint --max-line-length=90 *.py') },
      pytest: {
        withEnv([
          'GROOVY_HOME=test',
          'CODENARC_VERSION=test',
          'GMETRICS_VERSION=test',
          'SLF4J_VERSION=test',
        ]) {
          try {
            data.venv.run('python -m pytest -Werror -rXxs --junit-xml=results.xml')
          } finally {
            junit 'results.xml'
          }
        }
      },
      'SLF4J version check': {
        Set slf4jVersions = []
        readMavenPom(file: 'pom.xml').dependencies.findAll { dependency ->
          return dependency.artifactId.startsWith('slf4j')
        }.each { dependency ->
          slf4jVersions.add(dependency.version)
        }

        switch (slf4jVersions.size()) {
          case 0:
            error 'Could not find SLF4J libraries in pom.xml file'
            break
          case 1:
            echo 'All SLF4J versions match'
            break
          default:
            error 'pom.xml file contains mismatched SLF4J library versions'
            break
        }
      },
    )
  },
  publish: { data -> jupiter.publishDocs("${data['docs']}/", 'Ableton/groovylint') },
  deployWhen: { return devToolsProject.shouldDeploy() },
  deploy: { data ->
    String versionNumber = readFile('VERSION').trim()
    parallel(failFast: false,
      docker_hub: {
        docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-password') {
          try {
            // Try to pull the image tagged with the contents of the VERSION file. If that
            // call fails, then we should push this image to the registry.
            docker.image("abletonag/groovylint:${versionNumber}").pull()
          } catch (ignored) {
            data['image'].push(version.majorMinorVersion(versionNumber))
            data['image'].push(versionNumber)
            data['image'].push('latest')
          }
        }
      },
      version: {
        version.tag(versionNumber)
        version.forwardMinorBranch(versionNumber)
      },
    )
  },
)
