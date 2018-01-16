@Library(['ableton-utils@0.1.0', 'python-utils@0.3.0']) _

// Jenkins has some problems loading libraries from git references when they are
// named 'origin/branch_name' or 'refs/heads/branch_name'. Until this behavior
// is working, we need to strip those prefixes from the incoming HEAD_REF.
final BRANCH = "${env.HEAD_REF}".replace('origin/', '').replace('refs/heads/', '')
library "groovylint@${BRANCH}"


def addStages() {
  def image
  def venv = virtualenv.create(this, 'python3.6')

  runTheBuilds.timedStage('Checkout') {
    // Print out all environment variables for debugging purposes
    sh 'env'
    checkout scm
  }

  runTheBuilds.timedStage('Setup') {
    venv.run('pip install flake8 pydocstyle pylint')
  }

  runTheBuilds.timedStage('Build') {
    image = docker.build('abletonag/groovylint')
  }

  runTheBuilds.timedStage('Test') {
    parallel(failFast: false,
      flake8: {
        venv.run('flake8 --max-line-length=90 -v *.py')
      },
      groovylint: {
        // Use the Docker image created in the Build stage above. This ensures that the
        // we are checking our own Groovy code with the same library and image which would
        // be published to production.
        groovylint.check('./Jenkinsfile,**/*.groovy', image)
      },
      pydocstyle: {
        venv.run('pydocstyle -v *.py')
      },
      pylint: {
        venv.run('pylint --max-line-length=90 *.py')
      },
    )
  }

  if (env.HEAD_REF == 'refs/heads/master' || env.HEAD_REF == 'origin/master') {
    runTheBuilds.timedStage('Push') {
      def version = readFile('VERSION').trim()
      docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-password') {
        try {
          // Try to pull the image tagged with the contents of the VERSION file. If that
          // call fails, then we should push this image to the registry.
          docker.image(image.id + ':' + version).pull()
        } catch (ignored) {
          image.push(version)
        }
      }
    }
  }
}


runTheBuilds.runForSpecificBranches(runTheBuilds.COMMON_BRANCH_FILTERS, true) {
  node('generic-linux') {
    try {
      runTheBuilds.report('pending', env.CALLBACK_URL)
      addStages()
      runTheBuilds.report('success', env.CALLBACK_URL)
    }
    catch (error) {
      runTheBuilds.report('failure', env.CALLBACK_URL)
      throw error
    }
    finally {
      dir(env.WORKSPACE) {
        deleteDir()
      }
    }
  }
}
