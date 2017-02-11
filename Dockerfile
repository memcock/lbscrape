FROM gliderlabs/alpine:latest

ADD https://github.com/just-containers/s6-overlay/releases/download/v1.18.1.5/s6-overlay-amd64.tar.gz /tmp/s6-overlay-amd64.tar.gz
RUN tar xzf /tmp/s6-overlay-amd64.tar.gz -C /

RUN apk-install python3 postgresql-libs

ADD ./requirements.txt /tmp/requirements.txt
RUN apk --update add --virtual build-deps build-base postgresql-dev python3-dev && \
	python3 -m pip install -r /tmp/requirements.txt && \
	apk del build-deps

ADD ./s6 /etc
ADD . /app
WORKDIR /app
ENTRYPOINT ["/init"]
