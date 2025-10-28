#!/bin/bash

# Define variables
CONTAINER_NAME="selectielijsten"
STORAGE_ACCOUNT="wegwijsdevstorage"
SOURCE_DIR="$PWD/csv"
FILE_NAME="selectielijsten.csv"

# Specify the file to be uploaded
FILE="$SOURCE_DIR/$FILE_NAME"

# Check if the file exists
if [ -f "$FILE" ]; then
    echo "Uploading $FILE as $FILE_NAME..."

    # Upload command
    az storage blob upload \
        --account-name "$STORAGE_ACCOUNT" \
        --container-name "$CONTAINER_NAME" \
        --file "$FILE" \
        --name "$FILE_NAME" \
        --auth-mode login \
        --overwrite true

    echo "File uploaded successfully!"
else
    echo "File $FILE does not exist."
fi
