#!/bin/env python3
#
# Copyright (c) 2016 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""A small wrapper script to call CodeNarc and interpret its output."""

import sys

from groovylint import (
    parse_xml,
    run_codenarc,
)


if __name__ == '__main__':
    sys.exit(parse_xml.parse(run_codenarc.run(sys.argv[1:])))
