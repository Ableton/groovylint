/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */


/**
  * Lint Groovy files using CodeNarc with sensible defaults.
  *
  * @param args Map of arguments, which may include:
  *        <ul>
  *          <li>
  *            {@code includesPattern}: A comma-separated list of Ant-style file patterns
  *            to check. <strong>(required)</strong>.
  *          </li>
  *          <li>
  *            {@code groovylintImage}: If specified, use this Docker image handle to run
  *            {@code groovylint}. If {@code null}, then this function will try to fetch
  *            {@code groovylint} from Docker hub using the same version number
  *            corresponding to this library.
  *          </li>
  *        </ul>
  */
void check(Map args) {
  String dockerFlags = [
    '--entrypoint=""',
    "--volume=${env.WORKSPACE}:/ws",
  ].join(' ')

  String image = args.groovylintImage ?: 'abletonag/groovylint:latest'
  echo "Using groovylint Docker image: ${image}"

  String command = '/entrypoint.sh'
  if (args.includesPattern) {
    command += " '${args.includesPattern}'"
  }

  docker.image(image).inside(dockerFlags) {
    sh(
      label: 'Run CodeNarc',
      script: command
    )
  }
}
