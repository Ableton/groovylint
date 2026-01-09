# Copyright (c) 2026 Ableton AG, Berlin. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.
FROM gradle:jdk21-ubi AS build

ARG groovyVersion='unset'
ARG codeNarcVersion='unset'

COPY . /build
WORKDIR /build
RUN ./gradlew --no-daemon -PgroovyVersion=${groovyVersion} -PcodeNarcVersion=${codeNarcVersion} fatJar

FROM amazoncorretto:21-alpine

RUN mkdir /groovylint

COPY --from=build /build/build/libs/groovylint-*.jar /groovylint/groovylint.jar

ENTRYPOINT ["java", "-jar", "/groovylint/groovylint.jar"]
