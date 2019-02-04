# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Run CodeNarc and return the report file."""

import os
import subprocess
import sys


CODENARC_OUTPUT_FILE = 'codenarc-output.xml'


def _remove_report_file():
    if os.path.exists(CODENARC_OUTPUT_FILE):
        os.remove(CODENARC_OUTPUT_FILE)


def run(args):
    """Run CodeNarc on the given files and return the report file as a string."""
    # -rulesetfiles must not be an absolute path, only a relative one to the CLASSPATH
    codenarc_call = [
        '/usr/bin/codenarc.sh',
        '-rulesetfiles=ruleset.groovy',
        f'-report=xml:{CODENARC_OUTPUT_FILE}',
    ] + args

    output = subprocess.run(
        codenarc_call,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    )
    sys.stdout.buffer.write(output.stdout)

    # CodeNarc doesn't fail on compilation errors (?)
    if 'Compilation failed' in str(output.stdout):
        _remove_report_file()
        raise ValueError('Error when compiling files!')

    if output.returncode != 0:
        _remove_report_file()
        raise ValueError(f'CodeNarc finished with code: {output.returncode}')
    if not os.path.exists(CODENARC_OUTPUT_FILE):
        raise ValueError(f'Error: {CODENARC_OUTPUT_FILE} was not generated, aborting!')

    with open(CODENARC_OUTPUT_FILE) as xml_file:
        xml_text = xml_file.read()
    _remove_report_file()

    return xml_text
