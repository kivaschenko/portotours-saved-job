#!/bin/bash

# Define variables
CONTAINER_NAME="django-portotours"
TIMESTAMP=$(date +'%Y%m%d%H%M%S')
DUMP_FILE_NAME="dumpdb_$TIMESTAMP.json"
COMPRESSED_FILE_NAME="dumpdb_$TIMESTAMP.json.gz"
HOST_BACKUP_DIR="/etc/backup_django"
CONTAINER_DUMP_DIR="/app"
HOST_TEMP_DIR="/tmp"
LOG_FILE="/var/log/backup_db.log"
POSTMARK_TOKEN="e3a9f4b5-4a1a-43f1-8270-af8405499f87"
EMAIL_FROM="onedaytours@onedaytours.pt"
EMAIL_TO="civaschenko@yahoo.com,boan85@gmail.com"
DO_SPACES_BUCKET="portotoursmedia"
DO_SPACES_REGION="fra1"
DO_SPACES_ENDPOINT="https://$DO_SPACES_REGION.digitaloceanspaces.com"
S3_KEY="backups/$COMPRESSED_FILE_NAME"
RETENTION_DAYS=30

# Function to log message
log_message() {
  echo "$(date +'%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

send_email() {
  local subject=$1
  local message=$2

  curl -X POST "https://api.postmarkapp.com/email" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -H "X-Postmark-Server-Token: $POSTMARK_TOKEN" \
    -d '{
      "From": "'"$EMAIL_FROM"'",
      "To": "'"$EMAIL_TO"'",
      "Subject": "'"$subject"'",
      "TextBody": "'"$message"'"
    }'
}

# Run the dumpdata command inside the Docker container and save to a local temporary file
log_message "Running dumpdata command inside the Docker container..."
docker exec $CONTAINER_NAME python manage.py dumpdata --format=json --indent=4 > $HOST_TEMP_DIR/$DUMP_FILE_NAME

# Check if the dump file was created successfully
if [ -f "$HOST_TEMP_DIR/$DUMP_FILE_NAME" ]; then
  log_message "Database dump created successfully: $HOST_TEMP_DIR/$DUMP_FILE_NAME"

  # Compress the dump file
  log_message "Compressing the database dump file..."
  gzip -c $HOST_TEMP_DIR/$DUMP_FILE_NAME > $HOST_TEMP_DIR/$COMPRESSED_FILE_NAME

  # Move the compressed dump file to the backup directory
  mv $HOST_TEMP_DIR/$COMPRESSED_FILE_NAME $HOST_BACKUP_DIR/

  if [ $? -eq 0 ]; then
    log_message "Compressed database dump moved successfully to: $HOST_BACKUP_DIR/$COMPRESSED_FILE_NAME"
    # Upload the compressed dump file to DigitalOcean Spaces
    log_message "Uploading compressed dump file to DigitalOcean Spaces..."
    AWS_ACCESS_KEY_ID=DO00XNJ6TYVTDXKZ3TNH AWS_SECRET_ACCESS_KEY=Z/z+y6KJCHohD7fENfAZ4K9fARuPTj6yrddNprkzzHo aws s3 cp $HOST_BACKUP_DIR/$COMPRESSED_FILE_NAME s3://$DO_SPACES_BUCKET/$S3_KEY --endpoint-url $DO_SPACES_ENDPOINT

    if [ $? -eq 0 ]; then
            log_message "Compressed database dump uploaded successfully to DigitalOcean Spaces: s3://$DO_SPACES_BUCKET/$S3_KEY"
            send_email "Database Backup Success" "The database backup was created, compressed, and uploaded successfully to s3://$DO_SPACES_BUCKET/$S3_KEY."
        else
            log_message "Failed to upload compressed database dump to DigitalOcean Spaces"
            send_email "Database Backup Failure" "Failed to upload the compressed database dump to DigitalOcean Spaces."
        fi
  else
    log_message "Failed to move compressed database dump to backup directory"
    send_email "Database Backup Failure" "Failed to move the compressed database dump to the backup directory."
  fi

  # Clean up the uncompressed dump file
  rm $HOST_TEMP_DIR/$DUMP_FILE_NAME
else
  log_message "Failed to create database dump"
  send_email "Database Backup Failure" "Failed to create the database dump."
fi

# Delete old backups from DigitalOcean Spaces
log_message "Deleting backups older than $RETENTION_DAYS days from DigitalOcean Spaces..."
aws s3 ls s3://$DO_SPACES_BUCKET/backups/ --endpoint-url $DO_SPACES_ENDPOINT | while read -r line; do
  createDate=$(echo $line | awk '{print $1" "$2}')
  createDate=$(date -d"$createDate" +%s)
  olderThan=$(date -d"-$RETENTION_DAYS days" +%s)
  if [ $createDate -lt $olderThan ]; then
      fileName=$(echo $line | awk '{print $4}')
      if [ -n "$fileName" ]; then
          aws s3 rm s3://$DO_SPACES_BUCKET/backups/$fileName --endpoint-url $DO_SPACES_ENDPOINT
          log_message "Deleted $fileName from DigitalOcean Spaces"
      else
        log_message "Checking for Retention completed. No old backup files deleted from DigitalOcean Spaces"
      fi
  fi
done
