# Pull the base image
FROM python:3.10-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app/

# Update
RUN apt-get update
# GDAL
RUN apt-get install -y binutils libgdal-dev

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip setuptools
RUN pip install  --no-cache-dir -r requirements.txt

# Copy the Django project files
COPY . /app/

# Collect static files and migrate database
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

# Expose the port that Django will run on
EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "your_project.wsgi:application"]