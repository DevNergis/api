FROM alpine:latest

COPY . .
RUN apk add python3
RUN pip install -r requirements.txt

ENTRYPOINT [ "hypercorn main:app --bind 0.0.0.0:8070 --quic-bind 0.0.0.0:8070 --debug" ]
