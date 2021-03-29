#!/usr/bin/env python3
#
# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

"""A script to download JAR file dependencies for run_codenarc.py."""

import argparse
import logging
import os
import re
import shutil
import zipfile

from urllib.request import urlopen


def download_file(url, output_dir, force=False):
    """Download a file from a URL to the download directory."""
    output_file_name = url.split('/')[-1]
    output_file_path = os.path.join(output_dir, output_file_name)

    if force:
        try:
            os.remove(output_file_path)
        except FileNotFoundError:
            pass
    elif os.path.exists(output_file_path):
        logging.debug('%s already exists, skipping download', output_file_path)
        return output_file_path

    logging.debug('Downloading %s to %s', url, output_file_path)
    with urlopen(url) as response, open(output_file_path, 'wb') as out_fp:
        shutil.copyfileobj(response, out_fp)

    logging.info('Downloaded %s', output_file_name)
    return output_file_path


def fetch_jars(args):
    """Fetch JAR file dependencies."""
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    jar_urls = [
        (
            'https://github.com/CodeNarc/CodeNarc/releases/download'
            f'/v{args.codenarc_version}/CodeNarc-{args.codenarc_version}.jar'
        ),
        (
            'https://github.com/dx42/gmetrics/releases/download'
            f'/v{args.gmetrics_version}/GMetrics-{args.gmetrics_version}.jar'
        ),
        (
            f'https://repo1.maven.org/maven2/org/slf4j/slf4j-api/{args.slf4j_version}'
            f'/slf4j-api-{args.slf4j_version}.jar'
        ),
        (
            f'https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/{args.slf4j_version}'
            f'/slf4j-simple-{args.slf4j_version}.jar'
        ),
    ]

    for url in jar_urls:
        verify_jar(download_file(url, args.output_dir, args.force))


def jar_version_from_dockerfile(dockerfile, version_env_var):
    """Extract the version for a JAR file from the Dockerfile."""
    with open(dockerfile, 'r') as dockerfile_fp:
        for line in dockerfile_fp.readlines():
            line_match = re.search(f'ENV {version_env_var}=(.*)', line)
            if line_match:
                return line_match.group(1)

    raise ValueError(f'Could not find version for {version_env_var} in {dockerfile}')


def parse_args():
    """Parse arguments from the command line."""
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '--codenarc-version',
        help='Version of CodeNarc to download. Required if --dockerfile is not given.',
    )

    arg_parser.add_argument(
        '-d',
        '--dockerfile',
        help='Parse all versions from Dockerfile.',
    )

    arg_parser.add_argument(
        '--gmetrics-version',
        help='Version of GMetrics to download. Required if --dockerfile is not given.',
    )

    arg_parser.add_argument(
        '--slf4j-version',
        help='Version of SLF4J to download. Required if --dockerfile is not given.',
    )

    arg_parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Download JAR files regardless of whether or not they already exist.',
    )

    arg_parser.add_argument(
        '-o',
        '--output-dir',
        default=os.path.abspath(os.path.curdir),
        help='Directory to save JAR files to.',
    )

    arg_parser.add_argument(
        '-v', '--verbose', action='store_true', help='Show verbose output.'
    )

    args = arg_parser.parse_args()

    if args.dockerfile:
        args.codenarc_version = jar_version_from_dockerfile(
            args.dockerfile, 'CODENARC_VERSION'
        )
        args.gmetrics_version = jar_version_from_dockerfile(
            args.dockerfile, 'GMETRICS_VERSION'
        )
        args.slf4j_version = jar_version_from_dockerfile(
            args.dockerfile, 'SLF4J_VERSION'
        )
    else:
        assert args.codenarc_version
        assert args.gmetrics_version
        assert args.slf4j_version

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    return args


def verify_jar(file_path):
    """Verify that a file is a valid JAR file."""
    logging.debug('Verifying %s', file_path)
    with zipfile.ZipFile(file_path, 'r') as jar_file:
        if 'META-INF/MANIFEST.MF' not in jar_file.namelist():
            raise ValueError(f'{file_path} does not appear to be a valid JAR')


if __name__ == '__main__':
    fetch_jars(parse_args())
