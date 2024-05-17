#!/bin/bash

# Build Docker image
docker build -t terantbackend .

# Authenticate with Docker Hub and push the image
# echo "${DOCKER_PASSWORD}" | docker login -u "${DOCKER_USERNAME}" --password-stdin
docker tag terantbackend "anchalshivank/terantbackend:latest"
docker push "anchalshivank/terantbackend:latest"