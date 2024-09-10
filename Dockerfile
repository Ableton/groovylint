# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:4.0.22-jdk21-jammy

USER root

# For add-apt-repository
RUN apt-get update \
    && apt-get install -y software-properties-common=0.99.* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add deadsnakes and install Python 3.10
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update \
    && apt-get install -y python3.10=3.10.* --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY pom.xml /opt/
COPY ruleset.groovy /opt/resources/
COPY run_codenarc.py /opt/

WORKDIR /opt
RUN python3.10 run_codenarc.py --resources /opt/resources
RUN groupadd -r jenkins && useradd --no-log-init -r -g jenkins jenkins
USER jenkins

WORKDIR /ws

CMD ["python3.10", "/opt/run_codenarc.py"]
