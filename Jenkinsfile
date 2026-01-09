/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */

library(identifier: 'ableton-utils@0.28', changelog: false)
// Get groovylint library from current commit so it can test itself in this Jenkinsfile
library "groovylint@${params.JENKINS_COMMIT}"


devToolsProject.run(
  defaultBranch: 'main',
  build: { data ->
    String gitHash = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    String imageTag = "abletonag/groovylint:${gitHash}"
    sh(
      label: "Build groovylint Docker image",
      script: "./gradlew docker -PdockerImageTag=${imageTag}",
    )
    data['image'] = docker.image(imageTag)
  },
  test: { data ->
    stage('groovydoc') {
      data['docs'] = groovydoc.generate()
    }

    stage('groovylint docker') {
      // Use the Docker image created in the Build stage above. This ensures that the
      // we are checking our own Groovy code with the same library and image which
      // would be published to production.
      groovylint.check(
        includesPattern: './Jenkinsfile,**/*.groovy',
        groovylintImage: data['image'],
      )
    }

    stage('groovylint failure') {
      boolean failed = false
      try {
        groovylint.checkSingleFile(
          groovylintImage: data['image'], path: 'tests/failure.badgroovy',
        )
      } catch (error) {
        failed = true
      }
      if (!failed) {
        error 'groovylint did not fail when analyzing code with violations'
      }
    }

    stage('hadolint') {
      docker.image('hadolint/hadolint:v2.12.0-debian').inside {
        sh 'hadolint Dockerfile'
      }
    }
  },
  publish: { data -> jupiter.publishDocs("${data['docs']}/", 'Ableton/groovylint') },
  deploy: { data ->
    String lastTag = sh(
      returnStdout: true, script: 'git describe --tags --abbrev=0'
    ).trim()
    String body = sh(
      returnStdout: true, script: "git log --format='- %s (%h)' ${lastTag}..HEAD"
    )

    String versionNumber = readFile('VERSION').trim()
    parallel(
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
        if (version.tag(versionNumber)) {
          withCredentials([
            string(credentialsId: 'build-api-key', variable: 'BUILD_API_TOKEN'),
          ]) {
            List distFiles = findFiles(glob: '**/target/groovylint-*.jar') +
            gitHub.makeRelease(
              apiToken: BUILD_API_TOKEN,
              body: body,
              commitish: params.JENKINS_COMMIT,
              files: distFiles,
              name: versionNumber,
              owner: 'Ableton',
              publish: true,
              repository: 'groovylint',
              tagName: versionNumber,
            )
          }
        }
        version.forwardMinorBranch(versionNumber)
      },
    )
  },
)
