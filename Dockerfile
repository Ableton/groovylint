# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

FROM groovy:2.4-alpine

USER root

ENV CODENARC_VERSION=1.2.1
ENV SLF4J_VERSION=1.7.25
ENV GMETRICS_VERSION=1.0


# While the base Alpine image has a busybox-based wget, that version is not sophisticated
# enough to download from Sourceforge et. al.
RUN apk add --no-cache py3-setuptools=39.1.0-r0 python3=3.6.6-r0 wget=1.20.1-r0

RUN wget "https://netcologne.dl.sourceforge.net/project/codenarc/codenarc/CodeNarc%20$CODENARC_VERSION/CodeNarc-$CODENARC_VERSION.jar" \
    -P "/opt/CodeNarc-$CODENARC_VERSION"

RUN wget -q -O slf4j.tar.gz "https://www.slf4j.org/dist/slf4j-$SLF4J_VERSION.tar.gz" && \
    tar xvzf slf4j.tar.gz -C /opt && \
    rm slf4j.tar.gz

RUN wget "https://github.com/dx42/gmetrics/releases/download/v$GMETRICS_VERSION/GMetrics-$GMETRICS_VERSION.jar" \
    -P "/opt/GMetrics-$GMETRICS_VERSION"

COPY Pipfile /opt
COPY Pipfile.lock /opt
COPY codenarc.sh /usr/bin
COPY ruleset.groovy /opt/ruleset.groovy
COPY groovylint /opt/groovylint
COPY run_codenarc.py /opt/run_codenarc.py

WORKDIR /opt
RUN pip3 install --no-cache-dir pipenv==2018.11.26
RUN pipenv install --system --deploy

RUN adduser -D jenkins
USER jenkins

WORKDIR /ws

CMD ["python3", "/opt/run_codenarc.py"]
