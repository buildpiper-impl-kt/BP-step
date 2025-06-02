FROM aayush808/graviton:v2

ENV CODEBASE_DIR=""

COPY build.sh /build.sh
RUN chmod +x /build.sh

ENTRYPOINT ["/build.sh"]
