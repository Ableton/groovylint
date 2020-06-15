# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:jre8

USER root

ENV CODENARC_VERSION=1.6
ENV SLF4J_VERSION=1.7.29
ENV GMETRICS_VERSION=1.0

RUN apt-get update \
    && apt-get install -y python3.8=3.8.0-* python3-pip=9.0.1-* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /opt/
COPY fetch_jars.py /opt/
COPY ruleset.groovy /opt/
COPY run_codenarc.py /opt/

WORKDIR /opt
RUN pip3 install --no-cache-dir -r requirements.txt
RUN python3 fetch_jars.py --output-dir /opt \
  --codenarc-version $CODENARC_VERSION \
  --gmetrics-version $GMETRICS_VERSION \
  --slf4j-version $SLF4J_VERSION

RUN groupadd -r jenkins && useradd --no-log-init -r -g jenkins jenkins
USER jenkins

WORKDIR /ws

CMD ["python3", "/opt/run_codenarc.py"]
