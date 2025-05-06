FROM alpine:3.18

RUN apk add --no-cache curl python3 py3-pip bash \
 && pip install awscli \
 && rm -rf /var/cache/apk/*

COPY build.sh /build.sh
RUN chmod +x /build.sh

ENTRYPOINT ["/build.sh"]
