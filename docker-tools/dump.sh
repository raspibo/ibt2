#!/bin/sh

docker build -t ibt2-dump-and-restore .
docker run --name ibt2-dump --rm --network="ibt2_default" -v `pwd`:/data --link=ibt2_ibt2-mongo_1:ibt2-mongo ibt2-dump-and-restore --dump
