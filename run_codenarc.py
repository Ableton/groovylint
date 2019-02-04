#!/bin/env python3

"""A small wrapper script to call CodeNarc and interpret its output."""

import sys

from groovylint import (
    parse_xml,
    run_codenarc,
)


if __name__ == '__main__':
    sys.exit(parse_xml.parse(run_codenarc.run(sys.argv[1:])))
