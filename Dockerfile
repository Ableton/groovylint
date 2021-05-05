# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:jre8

USER root

RUN apt-get update \
    && apt-get install -y python3.8=3.8.* python3-pip=20.0.* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY resources/pom.xml /opt/
COPY resources/ruleset.groovy /opt/
COPY resources/run_codenarc.py /opt/

WORKDIR /opt
RUN python3.8 run_codenarc.py
RUN groupadd -r jenkins && useradd --no-log-init -r -g jenkins jenkins
USER jenkins

WORKDIR /ws

CMD ["python3.8", "/opt/run_codenarc.py"]
