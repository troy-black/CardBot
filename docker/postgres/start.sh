#!/bin/bash

docker volume create postgres-volume
docker run -d --name=postgres -p 5432:5432 -v postgres-volume:/var/lib/postgresql/data -e POSTGRES_USER=cardbot -e POSTGRES_PASSWORD=cardbot -e POSTGRES_DB=cardbot postgres
