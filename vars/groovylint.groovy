/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */


/**
 * Check a set of files with the {@code groovylint} Docker image.
 * @param args Map of arguments, which may include:
 *        <ul>
 *          <li>
 *            {@code includesPattern}: A comma-separated list of Ant-style file patterns
 *            to check. <strong>(required)</strong>.
 *          </li>
 *          <li>
 *            {@code codeNarcArgs}: Extra arguments to pass to CodeNarc. Callers will
 *            have to escape these arguments if necessary.
 *          </li>
 *          <li>
 *            {@code groovylintArgs}: Extra arguments to pass to {@code run_codenarc.py}.
 *            Callers will have to escape these arguments if necessary.
 *          </li>
 *          <li>
 *            {@code groovylintImage}: If specified, use this Docker image handle to run
 *            {@code groovylint}. If {@code null}, then this function will try to fetch
 *            {@code groovylint} from Docker hub using the same version number
 *            corresponding to this library.
 *          </li>
 *        </ul>
 */
void check(Map args = [:]) {
  assert args.includesPattern
  String includesPattern = args.includesPattern
  String groovylintArgs = args.groovylintArgs ?: ''
  String codeNarcArgs = args.codeNarcArgs ?: ''

  Object image = args.groovylintImage
  if (!image) {
    String version = env['library.groovylint.version']
    if (!version) {
      error 'Could not find groovylint version in environment'
    }
    image = docker.image("abletonag/groovylint:${version}")
    image.pull()
  }
  echo "Using groovylint Docker image: ${image.id}"

  image.inside {
    sh "python3 /opt/run_codenarc.py ${groovylintArgs} " +
      "-- -includes=${includesPattern} ${codeNarcArgs}"
  }
}


/**
 * Check a single file with the {@code groovylint} Docker image.
 * @param args Map of arguments, which may include:
 *        <ul>
 *          <li>
 *            {@code path}: Path to the single file to lint <strong>(required)</strong>.
 *          </li>
 *          <li>
 *            {@code groovylintArgs}: Extra arguments to pass to {@code run_codenarc.py}.
 *            Callers will have to escape these arguments if necessary.
 *          </li>
 *          <li>
 *            {@code groovylintImage}: If specified, use this Docker image handle to run
 *            {@code groovylint}. If {@code null}, then this function will try to fetch
 *            {@code groovylint} from Docker hub using the same version number
 *            corresponding to this library.
 *          </li>
 *        </ul>
 */
void checkSingleFile(Map args = [:]) {
  assert args.path

  Object image = args.groovylintImage
  if (!image) {
    String version = env['library.groovylint.version']
    if (!version) {
      error 'Could not find groovylint version in environment'
    }
    image = docker.image("abletonag/groovylint:${version}")
    image.pull()
  }
  echo "Using groovylint Docker image: ${image.id}"
  String groovylintArgs = args.groovylintArgs ?: ''

  image.inside {
    sh "python3 /opt/run_codenarc.py ${groovylintArgs} --single-file ${args.path}"
  }
}


/**
 * Helper function to find a JAR file under a given search path.
 *
 * When using Jenkinsfiles that import libraries, it may be necessary to provide CodeNarc
 * with a path to the corresponding JAR files (see the {@code --jar} argument in
 * {@code run_codenarc.py}). Assuming you know the name of the library, this function will
 * help you find its path on the remote host. Note that you'll need a {@code node} context
 * to use this function.
 *
 * @param searchPath Path to search for the JAR file in.
 * @param glob Ant-like glob to use to find the JAR file.
 */
String findJar(String searchPath, String glob) {
  String result
  dir(searchPath) {
    List jarFiles = findFiles(glob: glob)
    if (jarFiles.size() == 0) {
      error "Failed to find ${glob} in ${searchPath}"
    }
    else if (jarFiles.size() > 1) {
      error "Found multiple candidates for ${glob} in ${searchPath}"
    }
    result = "${searchPath}/${jarFiles[0].path}"
  }
  return result
}
