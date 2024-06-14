#!/bin/bash

# Define variables
CONTAINER_NAME="django-portotours"
LOG_FILE="/var/log/restore_db.log"

# Function to log messages
log_message() {
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Prompt the user for the dump file path
read -p "Enter the path to the gzip compressed dump file: " DUMP_FILE_PATH

# Validate the input
if [ ! -f "$DUMP_FILE_PATH" ]; then
    echo "The file '$DUMP_FILE_PATH' does not exist."
    exit 1
fi

DUMP_FILE_NAME=$(basename $DUMP_FILE_PATH)
DECOMPRESSED_FILE_NAME="${DUMP_FILE_NAME%.gz}"

# Log the start of the process
log_message "Starting database refresh process..."

# Copy the gzip compressed dump file into the Docker container
log_message "Copying compressed dump file into Docker container..."
docker cp $DUMP_FILE_PATH $CONTAINER_NAME:/app/$DUMP_FILE_NAME

# Flush the existing data (excluding the schema)
log_message "Flushing the existing data..."
docker exec $CONTAINER_NAME python manage.py flush --no-input

# Decompress the gzip file inside the Docker container
log_message "Decompressing the dump file..."
docker exec $CONTAINER_NAME bash -c "gunzip $DUMP_FILE_NAME"

# Load the decompressed data
log_message "Loading the new data..."
docker exec $CONTAINER_NAME python manage.py loaddata $DECOMPRESSED_FILE_NAME

# Check if the data was loaded successfully
if [ $? -eq 0 ]; then
    log_message "Data loaded successfully."
    send_email "Database Refresh Success" "The database has been refreshed successfully from the dump file."
else
    log_message "Failed to load data."
fi

# Clean up by removing the decompressed dump file from the container
log_message "Cleaning up..."
docker exec $CONTAINER_NAME rm $DECOMPRESSED_FILE_NAME

# Log the end of the process
log_message "Database refresh process completed."
