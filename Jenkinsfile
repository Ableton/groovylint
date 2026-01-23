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
  setup: { data ->
    data['groovy3Version'] = '3.0.22'
    data['groovy4Version'] = '4.0.22'

    [data.groovy3Version, data.groovy4Version].each { groovyVersion ->
      String groovyZip = "apache-groovy-binary-${groovyVersion}.zip"
      String mirrorHost = 'groovy.jfrog.io/artifactory/dist-release-local/groovy-zips'
      sh "curl -L -o ${groovyZip} https://${mirrorHost}/${groovyZip}"
      unzip(zipFile: groovyZip)
      sh "chmod 755 groovy-${groovyVersion}/bin/groovy"
    }
  },
  build: { data ->
    String gitHash = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
    data['image'] = docker.build("abletonag/groovylint:${gitHash}")
  },
  test: { data ->
    parallel(
      format: { sh 'uv run ruff format --check .' },
      groovydoc: { data['docs'] = groovydoc.generate() },
      'groovylint docker': {
        // Use the Docker image created in the Build stage above. This ensures that the
        // we are checking our own Groovy code with the same library and image which
        // would be published to production.
        groovylint.check(
          includesPattern: './Jenkinsfile,**/*.groovy',
          groovylintImage: data['image'],
        )
      },
      'groovylint failure': {
        boolean failed = false
        try {
          groovylint.checkSingleFile(
            groovylintImage: data['image'],
            path: 'tests/resources/failure.badgroovy',
          )
        } catch (error) {
          failed = true
        }
        if (!failed) {
          error 'groovylint did not fail when analyzing code with violations'
        }
      },
      'groovylint native': {
        // Run groovylint using the system Python. This is not a recommended use-case
        // for Jenkins CI installations, but is often more useful for developers running
        // groovylint locally.
        sh "python3 run_codenarc.py --verbose --resources ${env.WORKSPACE}/resources" +
          " --groovy-home ${pwd()}/groovy-${data.groovy3Version}" +
          ' -- -includes="./Jenkinsfile,**/*.groovy,**/*.gradle"'
        sh "python3 run_codenarc.py --verbose --resources ${env.WORKSPACE}/resources" +
          " --groovy-home ${pwd()}/groovy-${data.groovy4Version} --groovy4" +
          ' -- -includes="./Jenkinsfile,**/*.groovy,**/*.gradle"'
      },
      hadolint: {
        docker.image('hadolint/hadolint:v2.14.0-debian').inside {
          sh 'hadolint Dockerfile'
        }
      },
      pytest: {
        withEnv([
          'GROOVY_HOME=test',
          'CODENARC_VERSION=test',
          'GMETRICS_VERSION=test',
          'SLF4J_VERSION=test',
        ]) {
          junitUtils.run(testResults: 'results.xml') {
            sh 'uv run python -m pytest --junit-xml=results.xml'
          }
        }
      },
      ruff: { sh 'uv run ruff check --verbose .' },
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
            List distFiles = findFiles(glob: 'ruleset.groovy') +
              findFiles(glob: 'run_codenarc.py')
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
