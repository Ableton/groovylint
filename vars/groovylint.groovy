/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */

/**
 * Check a set of files with the {@code groovylint} Docker image. This function is
 * provided for backwards compatibility and will be removed in a future release.
 * @deprecated Use {@code check#Map}
 */
void check(String includesPattern, Object groovylintImage = null, String extraArgs = '') {
  check(
    includesPattern: includesPattern,
    groovylintImage: groovylintImage,
    extraArgs: extraArgs,
  )
}


/**
 * Check a set of files with the {@code groovylint} Docker image.
 * @param Map of arguments, which may include:
 *        <ul>
 *          <li>
 *            {@code includesPattern}: A comma-separated list of Ant-style file patterns
 *            to check <strong>(required)</strong>.
 *          </li>
 *          <li>
 *            {@code groovylintImage}: If specified, use this Docker image handle to run
 *            {@code groovylint}. Otherwise, this function will try to fetch
 *            {@code groovylint} from Docker hub (or a custom registry by using the {@code
 *            registry} argument) using the same version number corresponding to this
 *            library.
 *          </li>
 *          <li>
 *            {@code extraArgs}: Extra arguments to pass to CodeNarc. Callers will have to
 *            escape these arguments if necessary.
 *          </li>
 *          <li>{@code registry}: Use this Docker registry instead of Docker hub.</li>
 *        </ul>
 */
void check(Map args) {
  assert args
  assert args.includesPattern

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

  docker.withRegistry(args.registry ?: 'https://registry.hub.docker.com') {
    image.inside("-v ${env.WORKSPACE}:/ws") {
      sh "python3 /opt/run_codenarc.py -- -includes=${args.includesPattern}" +
        " ${args.extraArgs}"
    }
  }
}
