# Pull the base image
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update
RUN apt-get update
# GDAL
RUN apt-get install -y binutils libgdal-dev
# Set work directory
WORKDIR /app/

# Install dependencies
COPY requirements.txt /app
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt --no-cache-dir

# Copy project
COPY . /app/

CMD python3 manage.py migrate && python3 manage.py runserver 8000