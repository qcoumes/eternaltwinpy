#!/usr/bin/bash

yarn install
yarn etwin db check
yarn etwin db sync
yarn etwin start
