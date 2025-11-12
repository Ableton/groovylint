#!/usr/bin/env python3
#
# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

"""A small wrapper script to call CodeNarc and interpret its output."""

import argparse
import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

from typing import Dict, List, Optional
from urllib.error import HTTPError
from urllib.request import urlopen
from xml.etree import ElementTree as ET


log = logging.getLogger(__name__)


DEFAULT_REPORT_FILE = "codenarc-report.xml"
GROOVYLINT_HOME = os.path.dirname(os.path.realpath(__file__))
MAX_DOWNLOAD_ATTEMPTS = 5


class CodeNarcError(Exception):
    """Raised if CodeNarc failed to run."""

    def __init__(self, returncode: int) -> None:
        """Create a new instance of the CodeNarcError class."""
        super().__init__(f"CodeNarc failed with return code {returncode}")


class CodeNarcViolationsError(Exception):
    """Raised if CodeNarc violations were found."""

    def __init__(self, num_violations: int) -> None:
        """Create a new instance of the CodeNarcViolationsError class."""
        super().__init__()
        self.num_violations = num_violations


class CompilationError(Exception):
    """Raised if there was a compilation error."""

    def __init__(self) -> None:
        """Create a new instance of the CompilationError class."""
        super().__init__("Error when compiling files!")


class DownloadError(Exception):
    """Base class for download errors."""


class DownloadFailedError(DownloadError):
    """Raised if a download fails."""

    def __init__(self, url: str) -> None:
        """Create a new instance of the DownloadFailedError class."""
        super().__init__(f"Failed to download {url}")


class InvalidJARError(DownloadError):
    """Raised if a downloaded JAR file is invalid."""

    def __init__(self) -> None:
        """Create a new instance of the InvalidJARError class."""
        super().__init__("Invalid JAR file")


class MissingClasspathElementError(Exception):
    """Raised if a classpath element is missing."""

    def __init__(self, element: str) -> None:
        """Create a new instance of the MissingClasspathElementError class."""
        super().__init__(f"Classpath element {element} does not exist")


class MissingReportFileError(Exception):
    """Raised if the CodeNarc report file is missing."""

    def __init__(self, report_file: str) -> None:
        """Create a new instance of the MissingReportFileError class."""
        super().__init__(f"{report_file} was not generated, aborting!")


def _build_classpath(args: argparse.Namespace) -> str:
    """Construct the classpath to use for running CodeNarc."""
    codenarc_version = _codenarc_version(args.codenarc_version, is_groovy4=args.groovy4)
    classpath = [
        args.resources,
        f"{args.groovy_home}/lib/*",
        f"{args.resources}/CodeNarc-{codenarc_version}.jar",
        f"{args.resources}/GMetrics-{args.gmetrics_version}.jar",
        f"{args.resources}/activation-{args.activation_version}.jar",
        f"{args.resources}/jaxb-api-{args.jaxb_api_version}.jar",
        f"{args.resources}/slf4j-api-{args.slf4j_version}.jar",
        f"{args.resources}/slf4j-simple-{args.slf4j_version}.jar",
    ]

    for path in classpath:
        if not (os.path.exists(path) or path.endswith("*")):
            raise MissingClasspathElementError(path)

    return ":".join(classpath)


def _codenarc_version(version: str, *, is_groovy4: bool) -> str:
    """Get the CodeNarc version depending on the version of Groovy being used."""
    return f"{version}-groovy-4.0" if is_groovy4 else version


def _download_file(url: str, output_dir: str) -> str:
    """Download a file from a URL to the download directory."""
    output_file_name = url.split("/")[-1]
    output_file_path = os.path.join(output_dir, output_file_name)

    if os.path.exists(output_file_path):
        log.debug("%s already exists, skipping download", output_file_path)
        return output_file_path

    log.debug("Downloading %s to %s", url, output_file_path)
    try:
        with urlopen(url) as response, open(output_file_path, "wb") as out_fp:  # noqa: S310
            shutil.copyfileobj(response, out_fp)
    except HTTPError as http_error:
        log.error("Download of %s failed with code %d", url, http_error.code)
        raise DownloadFailedError(url) from http_error

    log.info("Downloaded %s", output_file_name)
    return output_file_path


def _download_jar_with_retry(url: str, output_dir: str) -> str:
    """Download a JAR file but retry in case of failure."""
    download_attempt = MAX_DOWNLOAD_ATTEMPTS
    sleep_duration = 1

    while download_attempt > 0:
        try:
            output_file_path = _download_file(url, output_dir)
            if not _is_valid_jar(output_file_path):
                log.warning("%s is not a valid JAR file", output_file_path)
                os.unlink(output_file_path)
                raise InvalidJARError

            return output_file_path
        except DownloadError:
            download_attempt -= 1
            sleep_duration *= 2
            log.debug("Sleeping %d seconds until next retry...", sleep_duration)
            time.sleep(sleep_duration)

    log.error("Failed to download %s after %d attempts", url, MAX_DOWNLOAD_ATTEMPTS)
    raise DownloadFailedError(url)


def _fetch_jars(args: argparse.Namespace) -> None:
    """Fetch JAR file dependencies."""
    if not os.path.exists(args.resources):
        os.mkdir(args.resources)

    codenarc_version = _codenarc_version(args.codenarc_version, is_groovy4=args.groovy4)
    jar_urls = [
        (
            "https://github.com/CodeNarc/CodeNarc/releases/download"
            f"/v{args.codenarc_version}/CodeNarc-{codenarc_version}.jar"
        ),
        (
            "https://github.com/dx42/gmetrics/releases/download"
            f"/v{args.gmetrics_version}/GMetrics-{args.gmetrics_version}.jar"
        ),
        (
            "https://repo1.maven.org/maven2/javax/activation/activation"
            f"/{args.activation_version}/activation-{args.activation_version}.jar"
        ),
        (
            "https://repo1.maven.org/maven2/javax/xml/bind/jaxb-api"
            f"/{args.jaxb_api_version}/jaxb-api-{args.jaxb_api_version}.jar"
        ),
        (
            f"https://repo1.maven.org/maven2/org/slf4j/slf4j-api/{args.slf4j_version}"
            f"/slf4j-api-{args.slf4j_version}.jar"
        ),
        (
            f"https://repo1.maven.org/maven2/org/slf4j/slf4j-simple/{args.slf4j_version}"
            f"/slf4j-simple-{args.slf4j_version}.jar"
        ),
    ]

    for url in jar_urls:
        _download_jar_with_retry(url, args.resources)


def _guess_groovy_home() -> Optional[str]:
    """Try to determine the location where Groovy is installed.

    :return: Path of the Groovy installation, or None if it can't be determined.
    """
    if "GROOVY_HOME" in os.environ:
        return os.environ["GROOVY_HOME"]

    if platform.system() == "Darwin":
        brew_groovy_home = "/usr/local/opt/groovysdk/libexec"
        if os.path.exists(brew_groovy_home):
            return brew_groovy_home
    if platform.system() == "Linux":
        # Many Linux distros have Groovy packages which use this location.
        linux_groovy_home = "/usr/share/groovy"
        if os.path.exists(linux_groovy_home):
            return linux_groovy_home

    return None


def _is_groovy4(groovy_home: str) -> bool:
    groovy_bin = os.path.join(groovy_home, "bin", "groovy")
    log.debug("Checking version for groovy binary %s", groovy_bin)
    groovy_version = subprocess.check_output([f"{groovy_bin}", "--version"]).decode()
    log.debug("Groovy version string: %s", groovy_version)
    return groovy_version.startswith("Groovy Version: 4.")


def _is_slf4j_line(line: str) -> bool:
    """Determine if a log line was produced by SLF4J.

    CodeNarc in some cases prints things to stdout, or uses multi-line logging calls which
    cannot be parsed correctly when we attempt to re-log them in _log_codenarc_output.
    """
    return isinstance(logging.getLevelName(line.split(" ")[0]), int)


def _is_valid_jar(file_path: str) -> bool:
    """Determine if a file is a valid JAR file."""
    log.debug("Verifying %s", file_path)
    try:
        with zipfile.ZipFile(file_path, "r") as jar_file:
            if "META-INF/MANIFEST.MF" not in jar_file.namelist():
                log.warning("%s does not appear to be a valid JAR", file_path)
                return False
    except zipfile.BadZipfile:
        log.warning("%s is not a valid zipfile", file_path)
        return False

    return True


def _log_codenarc_output(lines: List[str]) -> None:
    """Re-log lines from CodeNarc's output.

    This function takes a log line generated by CodeNarc and re-logs it with the logging
    framework. We take the log level, which is the first word of the line output, which
    can be used to determine the corresponding log level in Python's logging framework.
    """
    log_level = logging.INFO
    for line in lines:
        line_words = line.split(" ")
        if _is_slf4j_line(line):
            log_level = logging.getLevelName(line_words[0])
            log_message = " ".join(line_words[1:])
        else:
            # If we can't determine the log level, that likely means that this line is a
            # continuation of the previous line. This occurs when CodeNarc is logging
            # compilation messages, stacktraces, etc. In these cases, we should use the
            # same logging level as the last known line. Also, here we need to log the
            # entire line and not chop off the first word.
            log_message = line

        log.log(log_level, log_message)


def _print_violations(package_file_path: str, violations: List) -> int:
    """Print violations for a file.

    :param package_file_path: File path.
    :param violations: List of Violation elements.
    :return: Number of violations for the file.
    """
    for violation in violations:
        message_element = violation.find("Message")
        if message_element is not None:
            message = message_element.text
        else:
            message = "[empty message]"
        log.error(
            "%s:%s: %s: %s",
            package_file_path,
            violation.attrib["lineNumber"],
            violation.attrib["ruleName"],
            message,
        )

    return len(violations)


def _print_violations_in_files(package_path: str, files: List) -> int:
    """Print violations for each file in a package.

    :param package_path: Package path.
    :param files: List of File elements.
    :return: Number of violations for all files in the package.
    """
    num_violations = 0

    for package_file in files:
        package_file_name = f"{package_path}/{package_file.attrib['name']}"
        log.debug("Parsing violations in file: %s", package_file_name)
        num_violations += _print_violations(
            package_file_name, package_file.findall("Violation")
        )

    return num_violations


def _print_violations_in_packages(packages: List) -> int:
    """Print violations for each package in a list of packages.

    :param packages: List of Package elements.
    :return: Number of violations for all packages.
    """
    num_violations = 0

    for package in packages:
        # CodeNarc uses the empty string for the top-level package, which we translate to
        # '.', which prevents the violation files from appearing as belonging to '/'.
        package_path = package.attrib["path"]
        if not package_path:
            package_path = "."

        log.debug("Parsing violations in package: %s", package_path)
        num_violations += _print_violations_in_files(
            package_path, package.findall("File")
        )

    return num_violations


def parse_args(
    args: List[str], default_jar_versions: Dict[str, str]
) -> argparse.Namespace:
    """Parse arguments from the command line."""
    arg_parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    arg_parser.add_argument(
        "--activation-version",
        default=default_jar_versions["activation"],
        help="Activation Framework version to use (required for JDK11 + Groovy 3.x).",
    )

    arg_parser.add_argument(
        "--codenarc-version",
        default=default_jar_versions["CodeNarc"],
        help="CodeNarc version to use.",
    )

    arg_parser.add_argument(
        "--jaxb-api-version",
        default=default_jar_versions["jaxb-api"],
        help="JAXB API version to use (required for JDK11 + Groovy 3.x).",
    )

    arg_parser.add_argument(
        "--gmetrics-version",
        default=default_jar_versions["GMetrics"],
        help="GMetrics version to use.",
    )

    default_groovy_home = _guess_groovy_home()
    arg_parser.add_argument(
        "--groovy-home",
        default=default_groovy_home,
        required=(default_groovy_home is None),
        help="Groovy home directory.",
    )

    arg_parser.add_argument("--groovy4", action="store_true", help=argparse.SUPPRESS)

    arg_parser.add_argument(
        "--resources",
        default=os.path.join(GROOVYLINT_HOME, "resources"),
        help="Path to Groovylint resources directory.",
    )

    arg_parser.add_argument(
        "--single-file",
        help=(
            "When given, copy this file to a temporary directory and lint it. This may"
            " improve performance in large repositories. This option cannot be used with"
            ' "--" to pass options to CodeNarc.'
        ),
    )

    arg_parser.add_argument(
        "--slf4j-version",
        default=default_jar_versions["slf4j-api"],
        help="SLF4J version to use.",
    )

    arg_parser.add_argument(
        "-q",
        "--quiet",
        action="store_const",
        const=logging.WARNING,
        dest="log_level",
        help="Show less output",
    )

    arg_parser.add_argument(
        "-v",
        "--verbose",
        action="store_const",
        const=logging.DEBUG,
        dest="log_level",
        help="Show extra output",
    )

    arg_parser.add_argument(
        "codenarc_options",
        nargs="*",
        action="append",
        help='All options after "--" will be passed to CodeNarc',
    )

    args = arg_parser.parse_args(args)

    logging.basicConfig(
        format="%(levelname)s %(message)s",
        level=args.log_level or logging.INFO,
        stream=sys.stdout,
    )

    if not args.codenarc_version:
        sys.exit("Could not determine CodeNarc version")
    if not args.gmetrics_version:
        sys.exit("Could not determine GMetrics version")
    if not args.slf4j_version:
        sys.exit("Could not determine SLF4J version")

    args.groovy4 = _is_groovy4(args.groovy_home)

    if args.single_file and len(args.codenarc_options) > 1:
        arg_parser.error('--single-file cannot be used with "--"')

    args.codenarc_options = [
        option for sublist in args.codenarc_options for option in sublist
    ]

    return args


def parse_pom() -> Dict[str, str]:
    """Parse the pom.xml file and extract default JAR versions."""
    jar_versions = {}

    namespace = {"project": "http://maven.apache.org/POM/4.0.0"}
    pom_root = ET.parse(os.path.join(GROOVYLINT_HOME, "pom.xml")).getroot()
    for dependency in pom_root.find("project:dependencies", namespace):
        name = dependency.find("project:artifactId", namespace)
        version = dependency.find("project:version", namespace)
        jar_versions[name.text] = version.text

    return jar_versions


def parse_xml_report(xml_text: str) -> None:
    """Parse XML report text generated by CodeNarc.

    :param xml_text: Raw XML text of CodeNarc report.
    :return: 0 on success, 1 if any violations were found
    """
    log.debug("Parsing report XML")
    xml_doc = ET.fromstring(xml_text)

    package_summary = xml_doc.find("PackageSummary")
    log.info("Scanned %s files", package_summary.attrib["totalFiles"])
    total_violations = _print_violations_in_packages(xml_doc.findall("Package"))

    if total_violations != 0:
        raise CodeNarcViolationsError(total_violations)


def run_codenarc(args: argparse.Namespace, report_file: str | None = None) -> str:
    """Run CodeNarc on specified code.

    :param args: Parsed command line arguments.
    :param report_file: Name of report file to generate.
    :return: Raw XML text report generated by CodeNarc.
    """
    slf4j_log_level = {logging.DEBUG: "debug", logging.WARNING: "warn", None: "info"}[
        args.log_level
    ]

    with tempfile.TemporaryDirectory() as tempdir:
        if report_file is None:
            report_file = os.path.join(tempdir, DEFAULT_REPORT_FILE)

        if args.single_file:
            extra_args = [f"-sourcefiles=./{args.single_file}"]
        else:
            extra_args = args.codenarc_options

        # -rulesetfiles must not be an absolute path, only a relative one to the CLASSPATH
        codenarc_call = [
            "java",
            "-Dorg.slf4j.simpleLogger.showThreadName=false",
            f"-Dorg.slf4j.simpleLogger.defaultLogLevel={slf4j_log_level}",
            "-classpath",
            _build_classpath(args),
            "org.codenarc.CodeNarc",
            "-failOnError=true",
            "-rulesetfiles=ruleset.groovy",
            f"-report=xml:{os.path.abspath(report_file)}",
            *extra_args,
        ]

        log.debug("Executing CodeNarc command: %s", " ".join(codenarc_call))
        try:
            output = subprocess.run(
                codenarc_call,
                check=True,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as error:
            log.error("Failed executing command: %s", " ".join(codenarc_call))
            log.error(
                "CodeNarc exited with code %d: %s",
                error.returncode,
                error.stdout.decode(),
            )
            raise

        # Trim out empty lines which CodeNarc prints in its output.
        codenarc_output = [x for x in output.stdout.decode().split("\n") if x]
        # The last line of CodeNarc's output is (usually) a summary line, which is printed
        # to stdout and not through SLF4J. We save it to a variable and log it with an
        # assigned log level after printing out everything else. If CodeNarc fails due to
        # some other problem, it will not print this line, however.
        codenarc_summary = None
        if codenarc_output[-1].startswith("CodeNarc completed:"):
            codenarc_summary = codenarc_output.pop()

        _log_codenarc_output(codenarc_output)

        if codenarc_summary:
            log.debug(codenarc_summary)
        log.debug("CodeNarc returned with code %d", output.returncode)

        # CodeNarc doesn't fail on compilation errors, it just logs a message for each
        # file that could not be compiled and generates a report for everything else. It
        # also does not return a non-zero code in such cases. For our purposes, we want to
        # treat syntax errors (and similar problems) as a failure condition.
        if "Compilation failed" in str(output.stdout):
            raise CompilationError

        if output.returncode != 0:
            raise CodeNarcError(output.returncode)
        if not os.path.exists(report_file):
            raise MissingReportFileError(report_file)

        log.debug("Reading report file %s", report_file)
        with open(report_file, encoding="utf-8") as xml_file:
            xml_text = xml_file.read()

    return xml_text


if __name__ == "__main__":
    try:
        parsed_args = parse_args(sys.argv[1:], parse_pom())
        _fetch_jars(parsed_args)
        parse_xml_report(run_codenarc(parsed_args))
        log.info("No violations found")
    except CodeNarcViolationsError as exception:
        log.error("Found %s violation(s)", exception.num_violations)
        sys.exit(1)
