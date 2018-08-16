#!/bin/env python3

"""A small wrapper script to call CodeNarc and interpret its output."""

from html.parser import HTMLParser
import os
import subprocess
import sys


class CodeNarcHTMLParser(HTMLParser):
    """Custom HTML parser for CodeNarc output.

    Seeks through <td> tags until 'All Packages' is seen, then grabs the second <td>
    afterward. This is the 'Files with Violations' column for 'All Packages'.
    """

    saw_all_packages = False
    my_offset = 0
    current_tag = None
    violating_files = None

    def handle_starttag(self, tag, attrs):
        """Record when a tag is opened."""
        self.current_tag = tag

    def handle_data(self, data):
        """Process data if it's inside a <td>."""
        if self.violating_files is not None:
            # We already have what we need, stop processing.
            return
        if self.current_tag != 'td':
            # It's not a <td> tag, skip ahead.
            return
        if self.saw_all_packages:
            self.my_offset = self.my_offset + 1
        elif data == 'All Packages':
            self.saw_all_packages = True
        if self.my_offset == 2:
            if data == '-':
                data = '0'
            self.violating_files = int(data)

    def error(self, message):
        """Satisfy pylint as error is NotImplemented in HTMLParser."""
        raise message


def main():
    """Run CodeNarc on specified code."""
    parsed_args = sys.argv[1:]

    output_file = 'codenarc-output.html'

    # -rulesetfiles must not be an absolute path, only a relative one to the CLASSPATH
    codenarc_call = [
        '/usr/bin/codenarc',
        '-rulesetfiles=ruleset.groovy',
        '-report=html:%s' % output_file,
    ] + parsed_args

    output = subprocess.run(
        codenarc_call,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
    )
    sys.stdout.buffer.write(output.stdout)

    # CodeNarc doesn't fail on compilation errors (?)
    if 'Compilation failed' in str(output.stdout):
        print('Error when compiling files!')
        return 1

    print('Return code: %d' % output.returncode)

    if output.returncode != 0:
        return output.returncode
    if not os.path.exists(output_file):
        print('Error: %s was not generated, aborting!' % output_file)
        return 1

    parser = CodeNarcHTMLParser()
    with open(output_file) as file:
        parser.feed(file.read())

    if parser.violating_files is None:
        print('Error parsing CodeNarc output!')
        return 1

    error_file = 'groovylint-errors.html'
    if parser.violating_files > 0:
        print('Moving %s to %s.' % (output_file, error_file))
        os.rename(output_file, error_file)
        print('Error: %d files with violations. See %s for details.'
              % (parser.violating_files, error_file))
        return 1

    print('No violations detected!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
