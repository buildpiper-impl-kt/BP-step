FROM aayush808/graviton:v2

RUN yum install git -y

COPY build.sh /build.sh

RUN chmod +x /build.sh

ENTRYPOINT ["/build.sh"]
