/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */

library 'ableton-utils@0.19'
library 'python-utils@0.10'
// Get groovylint library from current commit so it can test itself in this Jenkinsfile
library "groovylint@${params.JENKINS_COMMIT}"


devToolsProject.run(
  setup: { data ->
    data['venv'] = virtualenv.create('python3.8')
    data.venv.run('pip install -r requirements-dev.txt -r requirements.txt')
  },
  build: { data ->
    data['gitHash'] = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    data['image'] = docker.build("groovylint:${data.gitHash}")
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
    docs.publish("${data['docs']}/", 'AbletonDevTools/groovylint')
  },
  deployWhen: { return devToolsProject.shouldDeploy() },
  deploy: { data ->
    String versionNumber = readFile('VERSION').trim()
    parallel(failFast: false,
      'docker registries': {
        Map registries = [
          'Ableton': [
            url: encryptedFile.read(
              path: 'ableton-registry.enc',
              credentialsId: 'devtools-data-password',
            ),
            org: 'devtools',
            credential: 'dtr-password',
          ],
          'Docker Hub': [
            url: 'https://registry.hub.docker.com',
            org: 'abletonag',
            credential: 'docker-hub-password',
          ],
        ]

        registries.each { registry, values ->
          echo "Publishing Docker image to ${registry}"
          docker.withRegistry(values.url, values.credential) {
            try {
              // Try to pull the image tagged with the contents of the VERSION file. If
              // that call fails, then we should push this image to the registry.
              docker.image("${values.org}/groovylint:${versionNumber}").pull()
            } catch (ignored) {
              data['image'].push(version.majorMinorVersion(versionNumber))
              data['image'].push(versionNumber)
              data['image'].push('latest')
            }
          }
        }
      },
      version: {
        version.tag(versionNumber)
        version.forwardMinorBranch(versionNumber)
      },
    )
  },
  cleanup: { data ->
    data.venv?.cleanup()
  },
)
