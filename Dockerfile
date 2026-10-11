FROM node:22-bookworm-slim AS frontend

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

COPY index.html vite.config.mjs ./
COPY src/ ./src/
COPY static/ ./static/
RUN npm run build

FROM python:3.11-slim-bookworm AS runtime
LABEL \
	maintainer="Davide Alberani <da@mimante.net>" \
	vendor="RaspiBO"

EXPOSE 3000

COPY requirements.txt /tmp/ibt2-requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes -r /tmp/ibt2-requirements.txt

WORKDIR /ibt2/

COPY ibt2.py monco.py utils.py LICENSE.txt ./
COPY --from=frontend /build/dist/ ./dist/
RUN mkdir ssl

ENTRYPOINT ["python", "./ibt2.py", "--mongo_url=mongodb://mongo"]
