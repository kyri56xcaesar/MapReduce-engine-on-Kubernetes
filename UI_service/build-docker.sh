#!/bin/bash
docker stop ui_service 2>/dev/null
docker build --tag=ui_service .
docker run -d -p 1338:1338 --rm --name=ui_service ui_service
