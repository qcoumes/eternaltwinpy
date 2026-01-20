FROM --platform=linux/amd64 node:lts-slim

ARG UID=1000
ARG GID=1000

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /www

RUN groupmod -g $GID node && usermod -u $UID -g $GID node

USER node
