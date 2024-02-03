#!/bin/bash

# Pull the latest Docker image
sudo docker pull kivaschenko/portotours:latest

# Stop and remove the existing Docker container
sudo docker stop django-portotours || true
sudo docker rm django-portotours || true

# Run the Docker container with the new image
sudo docker run -d --name django-portotours -p 8000:8000 kivaschenko/portotours:latest
