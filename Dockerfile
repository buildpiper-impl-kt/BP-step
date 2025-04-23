FROM alpine:3.20

WORKDIR /app

RUN apk add --no-cache bash tar

COPY build.sh /app/build.sh

RUN chmod +x /app/build.sh

ENTRYPOINT ["/app/build.sh"]

CMD ["/data/Install-Packages"]
