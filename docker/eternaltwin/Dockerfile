FROM node:lts

ARG UID=1000
ARG GID=1000

RUN groupmod -g $GID node && usermod -u $UID -g $GID node

RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y && chmod -R a+rwx /usr/local/cargo /usr/local/rustup

RUN mkdir -p /home/node/app
RUN git clone https://gitlab.com/eternaltwin/eternaltwin.git /home/node/app
WORKDIR /home/node/app

RUN yarn install
COPY eternaltwin.test.toml /home/node/app/eternaltwin.toml

RUN chown -R node:node /home/node/app
USER node

CMD ["yarn", "start:dev:back"]
