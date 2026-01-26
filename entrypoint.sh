#!/usr/bin/env bash

set -euo pipefail

codenarc_json="$(mktemp)"

_include_pattern="${1:-Jenkinsfile,*.gradle,**/*.groovy}"

java -jar /lib/codenarc-all.jar\
    -failOnError=true\
    -includes="${_include_pattern}"\
    -report=console:stdout\
    -report=json:${codenarc_json}\
    -rulesetfiles=file:/codenarc-rules/ruleset.groovy\
    -basedir=/ws

# Fail if there are files with linting violations.
jq --exit-status '.summary.filesWithViolations == 0' $codenarc_json >/dev/null
