FROM groovy:2.4

USER root

ENV CODENARC_VERSION=1.2.1
ENV SLF4J_VERSION=1.7.25
ENV GMETRICS_VERSION=1.0

RUN wget "https://netcologne.dl.sourceforge.net/project/codenarc/codenarc/CodeNarc%20$CODENARC_VERSION/CodeNarc-$CODENARC_VERSION.jar" \
    -P "/opt/CodeNarc-$CODENARC_VERSION"

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN wget -qO- "https://www.slf4j.org/dist/slf4j-$SLF4J_VERSION.tar.gz" | tar xvz -C /opt

RUN wget "https://github.com/dx42/gmetrics/releases/download/v$GMETRICS_VERSION/GMetrics-$GMETRICS_VERSION.jar" \
    -P "/opt/GMetrics-$GMETRICS_VERSION"

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3=3.5.3-1 \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

COPY codenarc /usr/bin
COPY ruleset.groovy /opt/ruleset.groovy
COPY run_codenarc.py /opt/run_codenarc.py

RUN useradd jenkins
USER jenkins

WORKDIR /ws

CMD ["python3", "/opt/run_codenarc.py"]
