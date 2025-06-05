FROM amazon/aws-cli

RUN yum update -y 
RUN yum install jq gettext -y

COPY build.sh .
RUN chmod +x build.sh

ENTRYPOINT ["/bin/bash", "./build.sh"]

