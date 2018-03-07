@SuppressWarnings('VariableTypeRequired') // For _ variable
@Library([
  'ableton-utils@0.8',
  'python-utils@0.8.0',
]) _

// Jenkins has some problems loading libraries from git references when they are
// named 'origin/branch_name' or 'refs/heads/branch_name'. Until this behavior
// is working, we need to strip those prefixes from the incoming HEAD_REF.
final String BRANCH = "${env.HEAD_REF}".replace('origin/', '').replace('refs/heads/', '')
library "groovylint@${BRANCH}"

import com.ableton.VirtualEnv as VirtualEnv


runTheBuilds.runDevToolsProject(
  setup: { data ->
    VirtualEnv venv = virtualenv.create('python3.6')
    venv.run('pip install flake8 pydocstyle pylint')
    data['venv'] = venv
  },
  build: { data ->
    data['image'] = docker.build('abletonag/groovylint')
  },
  test: { data ->
    VirtualEnv venv = data['venv']
    parallel(failFast: false,
      flake8: {
        venv.run('flake8 --max-line-length=90 -v *.py')
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
      pydocstyle: {
        venv.run('pydocstyle -v *.py')
      },
      pylint: {
        venv.run('pylint --max-line-length=90 *.py')
      },
    )
  },
  deploy: { data ->
    runTheBuilds.runForSpecificBranches(['master'], false) {
      String versionNumber = readFile('VERSION').trim()
      parallel(failFast: false,
        dtr: {
          docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-password') {
            try {
              // Try to pull the image tagged with the contents of the VERSION file. If
              // that call fails, then we should push this image to the registry.
              docker.image(data['image'].id + ':' + versionNumber).pull()
            } catch (ignored) {
              data['image'].push(versionNumber)
              data['image'].push('latest')
            }
          }
        },
        groovydoc: {
          docs.publish(data['docs'], 'AbletonDevTools/groovylint')
        },
        version: {
          version.tag(versionNumber)
          version.forwardMinorBranch(versionNumber)
        },
      )
    }
  },
)
