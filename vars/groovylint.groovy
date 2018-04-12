/**
 * Check a set of files with the {@code groovylint} Docker image.
 * @param includesPattern A comma-separated list of Ant-style file patterns to check.
 * @param groovylintImage If specified, use this Docker image handle to run
 *                        {@code groovylint}. If {@code null}, then this function will try
 *                        to fetch {@code groovylint} from Docker hub using the same
 *                        version number corresponding to this library.
 *                        (default: {@code null})
 */
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

  image.pull()
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
    error "Groovy style violations found, see ${env.BUILD_URL}artifact/${outputFile}"
  }
}
