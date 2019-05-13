/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */

// TODO: when the old Jenkins job has been retired, remove this block.
if (env.HEAD_REF || env.BASE_REF) {
  return
}

library 'ableton-utils@0.13'
// Get groovylint library from current commit so it can test itself in this Jenkinsfile
library "groovylint@${env.JENKINS_COMMIT}"


devToolsProject.run(
  setup: {
    sh 'pipenv sync --dev'
  },
  build: { data ->
    String gitHash = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    data['image'] = docker.build("abletonag/groovylint:${gitHash}")
  },
  test: { data ->
    parallel(failFast: false,
      flake8: {
        sh 'pipenv run flake8 -v'
      },
      groovydoc: {
        data['docs'] = groovydoc.generate()
      },
      groovylint: {
        // Use the Docker image created in the Build stage above. This ensures that the
        // we are checking our own Groovy code with the same library and image which would
        // be published to production.
        groovylint.check('./Jenkinsfile,**/*.groovy', data['image'])
      },
      hadolint: {
        docker.image('hadolint/hadolint:v1.13.0-debian').inside("-v ${pwd()}:/ws") {
          sh 'hadolint /ws/Dockerfile'
        }
      },
      pipenv: {
        sh 'pipenv check'
      },
      pydocstyle: {
        sh 'pipenv run pydocstyle -v'
      },
      pylint: {
        sh 'pipenv run pylint --max-line-length=90 *.py'
      },
      pytest: {
        withEnv([
          'GROOVY_HOME=test',
          'CODENARC_VERSION=test',
          'GMETRICS_VERSION=test',
          'SLF4J_VERSION=test',
        ]) {
          sh 'pipenv run python -m pytest -rXxs'
        }
      },
    )
  },
  publish: { data ->
    docs.publish(data['docs'], 'AbletonDevTools/groovylint')
  },
  deploy: { data ->
    if (runTheBuilds.isPushTo(['master'])) {
      String versionNumber = readFile('VERSION').trim()
      parallel(failFast: false,
        docker_hub: {
          docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-password') {
            try {
              // Try to pull the image tagged with the contents of the VERSION file. If
              // that call fails, then we should push this image to the registry.
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
    }
  },
  cleanup: {
    try {
      sh 'pipenv --rm'
    } catch (ignored) {}
  },
)
