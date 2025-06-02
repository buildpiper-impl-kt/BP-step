FROM aayush808/graviton:v2


RUN yum install -y git && \
    yum clean all && \
    rm -rf /var/cache/yum

ENV SOURCE_CODE=""

COPY build.sh /build.sh
RUN chmod +x /build.sh

ENTRYPOINT ["/build.sh"]
