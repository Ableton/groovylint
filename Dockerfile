# Copyright (c) 2019 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

FROM groovy:2.4-alpine

USER root

RUN apk add --no-cache py3-setuptools=39.1.0-r0 python3=3.6.6-r0

COPY Pipfile /opt/
COPY Pipfile.lock /opt/
COPY fetch_jars.py /opt/
COPY ruleset.groovy /opt/
COPY run_codenarc.py /opt/
COPY dependencies.yml /opt/

WORKDIR /opt
RUN pip3 install --no-cache-dir pipenv==2018.11.26
RUN pipenv install --system --ignore-pipfile
RUN python3 fetch_jars.py --dependencies-file /opt/dependencies.yml --output-dir /opt

RUN adduser -D jenkins
USER jenkins

WORKDIR /ws

CMD ["python3", "/opt/run_codenarc.py"]
