FROM node:lts-slim

ARG UID=1000
ARG GID=1000

RUN groupmod -g $GID node && usermod -u $UID -g $GID node

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /home/node/app
COPY eternaltwin /home/node/app
RUN chown -R node:node /home/node/app
WORKDIR /home/node/app

USER node
