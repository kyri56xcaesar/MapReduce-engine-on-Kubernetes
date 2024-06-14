#!/bin/bash
docker stop auth_service 2>/dev/null
docker build --tag=auth_service .
docker run -d -p 1337:1337 --rm --name=auth_service auth_service
