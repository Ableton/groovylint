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
import tarfile
import zipfile

import requests


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
    response = requests.get(url, stream=True)

    if not response.ok:
        raise ValueError(f'Failed to fetch {url}')

    with open(output_file_path, mode='wb') as output_file:
        for chunk in response.iter_content(chunk_size=256):
            output_file.write(chunk)

    logging.info('Downloaded %s', output_file_name)
    return output_file_path


def fetch_jars(args):
    """Fetch JAR file dependencies."""
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    jar_urls = [
        (
            'https://netcologne.dl.sourceforge.net/project/codenarc/codenarc'
            f'/CodeNarc%20{args.codenarc_version}/CodeNarc-{args.codenarc_version}.jar'
        ),
        (
            'https://github.com/dx42/gmetrics/releases/download'
            f'/v{args.gmetrics_version}/GMetrics-{args.gmetrics_version}.jar'
        ),
    ]

    # Note: The following URLs have been verified to be non-malicious, but you should be
    # careful when adding items to this list. These tarballs are extracted without
    # checking the paths, which can be dangerous according to the documentation for
    # tarfile.extractall().
    tar_urls = [f'http://www.slf4j.org/dist/slf4j-{args.slf4j_version}.tar.gz']

    for url in jar_urls:
        verify_jar(download_file(url, args.output_dir, args.force))

    for url in tar_urls:
        uncompress_tar(download_file(url, args.output_dir, args.force), args.output_dir)


def parse_args():
    """Parse arguments from the command line."""
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '--codenarc-version', help='Version of CodeNarc to download.', required=True
    )

    arg_parser.add_argument(
        '--gmetrics-version', help='Version of GMetrics to download.', required=True
    )

    arg_parser.add_argument(
        '--slf4j-version', help='Version of SLF4J to download.', required=True
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

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    return args


def uncompress_tar(file_path, output_dir):
    """Uncompress a tarball to the given output directory."""
    logging.debug('Uncompressing %s', file_path)
    with tarfile.open(file_path) as tar:
        tar.extractall(path=output_dir)
    logging.info('Uncompressed %s', file_path)


def verify_jar(file_path):
    """Verify that a file is a valid JAR file."""
    logging.debug('Verifying %s', file_path)
    with zipfile.ZipFile(file_path, 'r') as jar_file:
        if 'META-INF/MANIFEST.MF' not in jar_file.namelist():
            raise ValueError(f'{file_path} does not appear to be a valid JAR')


if __name__ == '__main__':
    fetch_jars(parse_args())
