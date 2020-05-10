FROM alpine
LABEL \
	maintainer="Davide Alberani <da@erlug.linux.it>" \
	vendor="RaspiBO"

EXPOSE 3000

RUN \
	apk add --no-cache \
		nodejs \
		npm \
		py3-pip \
		py3-tornado && \
	pip3 install pymongo

COPY . /ibt2

WORKDIR /ibt2/

RUN \
	npm install && \
	node build/build.js && \
	rm -rf node_modules

ENTRYPOINT ["./ibt2.py", "--mongo_url=mongodb://mongo", "--debug"]
