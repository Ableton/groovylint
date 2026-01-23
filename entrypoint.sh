#!/usr/bin/env bash

set -euo pipefail

codenarc_json="$(mktemp)"

java -jar /lib/codenarc-all.jar\
    -failOnError=true\
    -includes=Jenkinsfile,*.gradle,**/*.groovy\
    -report=console:stdout\
    -report=json:${codenarc_json}\
    -rulesetfiles=file:/codenarc-rules/ruleset.groovy\
    -basedir=/ws

# Fail if there are files with linting violations.
jq --exit-status '.summary.filesWithViolations == 0' $codenarc_json >/dev/null
