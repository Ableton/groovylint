# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

"""Tests for run_codenarc script."""

import os
import subprocess

from unittest.mock import patch

import pytest

from run_codenarc import run_codenarc


def _report_file_contents(name):
    with open(_report_file_path(name)) as report_file:
        return report_file.read()


def _report_file_path(name):
    return os.path.join(os.path.dirname(__file__), 'xml-reports', name)


@patch('os.remove')
def test_run_codenarc(remove_mock):
    """Test that run_codenarc exits without errors if CodeNarc ran successfully."""
    with patch('subprocess.run') as subprocess_mock:
        subprocess_mock.return_value = subprocess.CompletedProcess(
            args='',
            returncode=0,
            stdout=b'',
        )

        output = run_codenarc(args=[], report_file=_report_file_path('success.xml'))

    assert _report_file_contents('success.xml') == output


def test_run_codenarc_compilation_failure():
    """Test that run_codenarc raises an error if CodeNarc found compilation errors."""
    with patch('subprocess.run') as subprocess_mock:
        subprocess_mock.return_value = subprocess.CompletedProcess(
            args='',
            returncode=0,
            stdout=b"""
                [main] INFO org.codenarc.source.AbstractSourceCode - Compilation
                failed because of [org.codehaus.groovy.control.CompilationErrorsException]
                with message: [startup failed:
            """,
        )

        with pytest.raises(ValueError):
            run_codenarc(args=[])


def test_run_codenarc_failure_code():
    """Test that run_codenarc raises an error if CodeNarc failed to run."""
    with patch('subprocess.run') as subprocess_mock:
        subprocess_mock.return_value = subprocess.CompletedProcess(
            args='',
            returncode=1,
            stdout=b'',
        )

        with pytest.raises(ValueError):
            run_codenarc(args=[])


def test_run_codenarc_no_report_file():
    """Test that run_codenarc raises an error if CodeNarc did not produce a report."""
    with patch('subprocess.run') as subprocess_mock:
        subprocess_mock.return_value = subprocess.CompletedProcess(
            args='',
            returncode=0,
            stdout=b'',
        )

        with pytest.raises(ValueError):
            run_codenarc(args=[], report_file='invalid')
