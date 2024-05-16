# Pull the base image
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE portotours.production
ENV STRIPE_PUBLIC_KEY=$STRIPE_PUBLIC_KEY
ENV STRIPE_SECRET_KEY=$STRIPE_SECRET_KEY

# Set work directory
WORKDIR /app/

# Add GDAL libs
RUN apt-get update \
    && apt-get install -y sudo \
    && sudo apt-get install -y binutils libgdal-dev \
    && sudo apt-get install -y redis-server \
    && sudo apt-get install vim \
    && sudo apt-get clean \
    && sudo rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . /app/
# Create logfile
RUN mkdir -p /app/log && touch /app/log/portotours.log

# Collect static files and migrate database
RUN python manage.py collectstatic --noinput
#RUN python manage.py migrate

# Expose the port that Django will run on
EXPOSE 8000

# Copy the startup script
COPY start.sh /app/start.sh

# Make the startup script executable
RUN chmod +x /app/start.sh

# Execute the startup script
CMD ["/app/start.sh"]
