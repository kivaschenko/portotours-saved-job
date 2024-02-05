# Pull the base image
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app/

# Add GDAL libs
RUN apt-get update \
    && apt-get install -y sudo \
    && sudo apt-get install -y binutils libgdal-dev \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools
RUN pip install  --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . /app/

# Collect static files and migrate database
RUN python manage.py collectstatic --noinput
RUN python manage.py makemigrations
RUN python manage.py migrate

# Expose the port that Django will run on
EXPOSE 8000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:8000", "portotours.wsgi:application"]