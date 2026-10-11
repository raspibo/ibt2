FROM node:22-bookworm-slim
LABEL \
	maintainer="Davide Alberani <da@mimante.net>" \
	vendor="RaspiBO"

EXPOSE 3000

RUN \
	apt-get update && \
	apt-get install --no-install-recommends -y \
		python3-pip \
		python3-venv && \
	rm -rf /var/lib/apt/lists/* && \
	python3 -m venv /opt/venv

COPY requirements.txt /tmp/ibt2-requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir --require-hashes -r /tmp/ibt2-requirements.txt

COPY . /ibt2

WORKDIR /ibt2/

RUN \
	npm ci --legacy-peer-deps && \
	npm run build && \
	rm -rf node_modules

ENTRYPOINT ["/opt/venv/bin/python", "./ibt2.py", "--mongo_url=mongodb://mongo"]
