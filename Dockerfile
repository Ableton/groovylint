# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:2.4-alpine

USER root

ENV CODENARC_VERSION=1.3
ENV SLF4J_VERSION=1.7.25
ENV GMETRICS_VERSION=1.0

RUN apk add --no-cache py3-setuptools~=39.1 python3~=3.6

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

RUN adduser -D jenkins
USER jenkins

WORKDIR /ws

CMD ["python3", "/opt/run_codenarc.py"]
