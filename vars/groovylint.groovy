@SuppressWarnings('MethodParameterTypeRequired')
void check(String includesPattern, groovylintImage = null) {
  @SuppressWarnings('VariableTypeRequired')
  def image = groovylintImage
  if (!image) {
    String version = env['library.groovylint.version']
    if (!version) {
      error 'Could not find groovylint version in environment'
    }
    image = docker.image("abletonag/groovylint:${version}")
  }
  echo "Using groovylint Docker image: ${image.id}"

  image.withRun(
      "-v ${env.WORKSPACE}:/ws",
      "python3 /opt/run_codenarc.py -includes=${includesPattern}",
  ) { c ->
    sh "docker wait ${c.id}"
    sh "docker logs ${c.id}"
  }

  String outputFile = 'groovylint-errors.html'
  if (fileExists(outputFile)) {
    archive outputFile
    error "Groovy style violations found, see ${outputFile}"
  }
}
