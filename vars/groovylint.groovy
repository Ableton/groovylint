/*
 * Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
 *
 * Use of this source code is governed by a MIT-style
 * license that can be found in the LICENSE file.
 */


/**
  * Lint Groovy files using CodeNarc with sensible defaults.
  *
  * @param dockerImageId, if unset latest is used.
  */
void check(String dockerImageId) {
  String dockerFlags = [
    '--entrypoint=""',
    "--volume=${env.WORKSPACE}:/ws",
  ].join(' ')

  String image = dockerImageId ?: 'abletonag/codenarc:latest'
  echo "Using groovylint Docker image: ${image}"

  docker.image(image).inside(dockerFlags) {
    sh(
      label: 'Run CodeNarc',
      script: '/entrypoint.sh'
    )
  }
}
