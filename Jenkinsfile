@SuppressWarnings('VariableTypeRequired') // For _ variable
@Library([
  'ableton-utils@0.8',
  'python-utils@0.9',
]) _

// Jenkins has some problems loading libraries from git references when they are
// named 'origin/branch_name' or 'refs/heads/branch_name'. Until this behavior
// is working, we need to strip those prefixes from the incoming HEAD_REF.
String branch
if (env.CHANGE_BRANCH) {
  // Defined for PR-triggered events for a multibranch pipeline job
  branch = env.CHANGE_BRANCH
} else if (env.BRANCH_NAME) {
  // Defined for all event triggers in a multibranch pipeline job
  branch = env.BRANCH_NAME
} else if (env.HEAD_REF) {
  // Defined for a runthebuilds parameterized job
  branch = "${env.HEAD_REF}".replace('origin/', '').replace('refs/heads/', '')
}
library "groovylint@${branch}"

import com.ableton.VersionTagger as VersionTagger
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
      hadolint: {
        docker.image('hadolint/hadolint').inside("-v ${pwd()}:/ws") {
          // See comment in Dockerfile explaining why this rule is ignored
          sh 'hadolint --ignore DL3002 /ws/Dockerfile'
        }
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
              data['image'].push(VersionTagger.majorMinorVersion(versionNumber))
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
  cleanup: { data ->
    if (data?.venv) {
      data.venv.cleanup()
    }
  },
)
