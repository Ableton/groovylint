#!/bin/sh
#
# Copyright (c) 2016 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

SLF4J_JAR=/opt/slf4j-$SLF4J_VERSION/slf4j-api-$SLF4J_VERSION.jar:/opt/slf4j-$SLF4J_VERSION/slf4j-simple-$SLF4J_VERSION.jar
GMETRICS_JAR=/opt/GMetrics-$GMETRICS_VERSION/GMetrics-$GMETRICS_VERSION.jar
CODENARC_JAR=/opt/CodeNarc-$CODENARC_VERSION/CodeNarc-$CODENARC_VERSION.jar
GROOVY_JAR=$GROOVY_HOME/embeddable/groovy-all-$GROOVY_VERSION.jar

java \
  -classpath /opt/:"$SLF4J_JAR:$GMETRICS_JAR:$CODENARC_JAR:$GROOVY_JAR" \
  org.codenarc.CodeNarc "$@"
