# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:jre8

USER root

ENV CODENARC_VERSION=2.0.0
ENV SLF4J_VERSION=1.7.30
ENV GMETRICS_VERSION=1.1

RUN apt-get update \
    && apt-get install -y python3.8=3.8.* python3-pip=20.0.* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY fetch_jars.py /opt/
COPY ruleset.groovy /opt/resources/
COPY run_codenarc.py /opt/

WORKDIR /opt
RUN python3.8 fetch_jars.py --output-dir /opt/resources \
  --codenarc-version $CODENARC_VERSION \
  --gmetrics-version $GMETRICS_VERSION \
  --slf4j-version $SLF4J_VERSION

RUN groupadd -r jenkins && useradd --no-log-init -r -g jenkins jenkins
USER jenkins

WORKDIR /ws

CMD ["python3.8", "/opt/run_codenarc.py"]
