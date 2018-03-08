FROM groovy:2.4

# This line requires that we ignore the hadolint violation DL3002
# We need to switch to the root user to run apt-get, which is a limitation of the Ubuntu
# image, which the groovy image is based upon.
USER root

ENV CODENARC_VERSION=1.1
ENV SLF4J_VERSION=1.7.25
ENV GMETRICS_VERSION=1.0

RUN wget "https://netcologne.dl.sourceforge.net/project/codenarc/codenarc/CodeNarc%20$CODENARC_VERSION/CodeNarc-$CODENARC_VERSION.jar" \
    -P "/opt/CodeNarc-$CODENARC_VERSION"

RUN wget -qO- "https://www.slf4j.org/dist/slf4j-$SLF4J_VERSION.tar.gz" | tar xvz -C /opt

RUN wget "https://github.com/dx42/gmetrics/releases/download/v$GMETRICS_VERSION/GMetrics-$GMETRICS_VERSION.jar" \
    -P "/opt/GMetrics-$GMETRICS_VERSION"

RUN apt-get update
RUN apt-get install -y python3

COPY codenarc /usr/bin
ADD ruleset.groovy /opt/ruleset.groovy
ADD run_codenarc.py /opt/run_codenarc.py

RUN useradd jenkins
USER jenkins

WORKDIR /ws

CMD ["python3", "/opt/run_codenarc.py"]
