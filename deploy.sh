#!/bin/bash

# Pull the latest Docker image
docker pull kivaschenko/portotours:latest

# Stop and remove the existing Docker container
docker stop django-portotours || true
docker rm django-portotours || true

# Run the Docker container with the new image
docker run -d --name django-portotours -p 8000:8000 kivaschenko/portotours:latest
