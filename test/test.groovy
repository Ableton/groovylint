#!groovy

def call() {
  if (artifactoryTarget == null) {
    try {
      artifactoryTarget = (env.JOB_NAME =~ /^([^\/\s]*\/[^\/\s]*)/)[0][1]
    } catch (all) {
      artifactoryTarget = env.JOB_NAME
    }
  }

  // Artifactory server defined in Jenkins configuration
  def server = Artifactory.server 'crc-artifactory'

  // Define package information for upload
  def packageInfo = """{
    "files": [
      {
         "pattern": "${filePattern}",
         "target": "${artifactoryTarget}/"
      }
    ]
  }"""

  // Actual upload into Artifactory
  script {
    println "Artifactory target: ${artifactoryTarget}"
    def buildInfo = server.upload(packageInfo)
    server.publishBuildInfo(buildInfo)
  }
  try {}
  catch {}
}
