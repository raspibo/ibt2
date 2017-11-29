FROM node
LABEL \
	maintainer="Davide Alberani <da@erlug.linux.it>" \
	vendor="RaspiBO"

EXPOSE 3000

RUN \
	apt-get update && \
	apt-get -y --no-install-recommends install \
		nodejs \
		npm \
		python3-pymongo \
		python3-tornado && \
	rm -rf /var/lib/apt/lists/*

COPY . /ibt2

WORKDIR /ibt2/

RUN \
	npm install && \
	nodejs build/build.js && \
	rm -rm node_modules

ENTRYPOINT ["./ibt2.py", "--mongo_url=mongodb://mongo", "--debug"]
