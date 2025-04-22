FROM alpine:3.20

WORKDIR /app

RUN apk add --no-cache bash tar

COPY demo.sh /app/demo.sh

RUN chmod +x /app/demo.sh

ENTRYPOINT ["/app/demo.sh"]

CMD ["/data/Install-Packages"]
