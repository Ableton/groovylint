FROM codenarc/codenarc:3.7.0-groovy-4.0.24

RUN apt-get update\
    && apt-get install -y --no-install-recommends jq="1.6*"\
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /codenarc-rules
COPY ruleset.groovy /codenarc-rules/ruleset.groovy
COPY entrypoint.sh /entrypoint.sh

WORKDIR /ws

ENTRYPOINT ["/entrypoint.sh"]
