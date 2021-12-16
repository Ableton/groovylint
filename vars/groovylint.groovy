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
 *            {@code extraArgs}: Extra arguments to pass to CodeNarc. Callers will have to
 *            escape these arguments if necessary.
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
  String extraArgs = args.extraArgs ?: ''

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
    sh "python3 /opt/run_codenarc.py -- -includes=${includesPattern} ${extraArgs}"
  }
}


/**
 * Check a set of files with the {@code groovylint} Docker image.
 * @param includesPattern A comma-separated list of Ant-style file patterns to check.
 * @param groovylintImage If specified, use this Docker image handle to run
 *        {@code groovylint}. If {@code null}, then this function will try to fetch
 *        {@code groovylint} from Docker hub using the same version number corresponding
 *        to this library. (default: {@code null})
 * @param extraArgs Extra arguments to pass to CodeNarc. Callers will have to escape these
 *        arguments if necessary.
 * @deprecated Use check(Map) instead.
 */
void check(String includesPattern, Object groovylintImage = null, String extraArgs = '') {
  check(
    extraArgs: extraArgs,
    includesPattern: includesPattern,
    groovylintImage: groovylintImage,
  )
}


/**
 * Check a single file with the {@code groovylint} Docker image.
 * @param args Map of arguments, which may include:
 *        <ul>
 *          <li>
 *            {@code path}: Path to the single file to lint <strong>(required)</strong>.
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

  image.inside {
    sh "python3 /opt/run_codenarc.py --single-file ${args.path}"
  }
}
