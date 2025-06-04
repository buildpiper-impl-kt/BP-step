
FROM alpine:3.20 AS builder


RUN apk add --no-cache \
    openjdk17 \
    python3 \
    py3-pip \
    maven \
    binutils \
    unzip \
    curl \
    bash 

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk
ENV PATH=$PATH:$JAVA_HOME/bin

WORKDIR /app


RUN curl -L -o graviton.zip https://github.com/aws/porting-advisor-for-graviton/archive/refs/heads/main.zip && \
    unzip graviton.zip && \
    mv porting-advisor-for-graviton-main/src ./src && \
    mv porting-advisor-for-graviton-main/build.sh ./build.sh && \
    mv porting-advisor-for-graviton-main/setup-environment.sh ./setup-environment.sh && \
    mv porting-advisor-for-graviton-main/getBinaryName.sh ./getBinaryName.sh && \
    mv porting-advisor-for-graviton-main/requirements-build.txt ./requirements-build.txt


RUN python3 -m venv /app/.venv && \
    . /app/.venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements-build.txt && \
    pip install xlsx2csv && \
    FILE_NAME=porting-advisor ./build.sh && \
    mv dist/porting-advisor /opt/porting-advisor

FROM alpine:3.20 AS runtime

RUN apk add --no-cache openjdk17 python3 py3-pip bash

RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install xlsx2csv

ENV PATH="/venv/bin:$PATH"

COPY --from=builder /opt/porting-advisor /usr/bin/porting-advisor
COPY build.sh .

RUN chmod +x build.sh

ENTRYPOINT ["./build.sh"]
