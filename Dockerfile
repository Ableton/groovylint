# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:4.0.33-jdk21-noble

USER 0

RUN sed --in-place -e 's/archive.ubuntu.com/de.archive.ubuntu.com/g' /etc/apt/sources.list

# For add-apt-repository
RUN apt-get update \
    && apt-get install -y software-properties-common=0.99.* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python 3.12
RUN apt-get update \
    && apt-get install -y python3.12=3.12.* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pom.xml /opt/
COPY resources/WorkflowScriptStub.jar /opt/resources/
COPY resources/ruleset.groovy /opt/resources/
COPY run_codenarc.py /opt/

WORKDIR /opt
RUN python3.12 run_codenarc.py --resources /opt/resources
RUN groupadd -r jenkins && useradd -u 1337 --no-log-init -r -g jenkins jenkins
USER 1337

WORKDIR /ws

CMD ["python3.12", "/opt/run_codenarc.py"]
