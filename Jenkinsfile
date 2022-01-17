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
    data['venv'] = virtualenv.create('python3.8')
    data.venv.run('pip install -r requirements-dev.txt')
  },
  build: { data ->
    String gitHash = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    data['image'] = docker.build("abletonag/groovylint:${gitHash}")
  },
  test: { data ->
    parallel(failFast: false,
      black: {
        data.venv.run('black --check .')
      },
      flake8: {
        data.venv.run('flake8 -v')
      },
      groovydoc: {
        data['docs'] = groovydoc.generate()
      },
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
          ' -- -includes="./Jenkinsfile,**/*.groovy,**/*.gradle"'
      },
      hadolint: {
        docker.image('hadolint/hadolint:v1.13.0-debian').inside("-v ${pwd()}:/ws") {
          sh 'hadolint /ws/Dockerfile'
        }
      },
      pydocstyle: {
        data.venv.run('pydocstyle -v')
      },
      pylint: {
        data.venv.run('pylint --max-line-length=90 *.py')
      },
      pytest: {
        withEnv([
          'GROOVY_HOME=test',
          'CODENARC_VERSION=test',
          'GMETRICS_VERSION=test',
          'SLF4J_VERSION=test',
        ]) {
          try {
            data.venv.run('python -m pytest -rXxs --junit-xml=results.xml')
          } finally {
            junit 'results.xml'
          }
        }
      },
    )
  },
  publish: { data ->
    jupiter.publishDocs("${data['docs']}/", 'AbletonDevTools/groovylint')
  },
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
