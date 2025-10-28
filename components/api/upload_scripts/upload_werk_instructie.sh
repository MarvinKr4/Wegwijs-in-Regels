#!/bin/bash

# Define variables
CONTAINER_NAME="werk-instructie"
STORAGE_ACCOUNT="wegwijsdevstorage"
SOURCE_DIR="$PWD/werk_instructie/instructie.json"

# Upload files recursively
find "$SOURCE_DIR" -type f | while read -r FILE; do
    FILENAME=$(basename "$FILE")

    echo "Uploading $FILE as $FILENAME..."

    # Upload command
    az storage blob upload \
        --account-name "$STORAGE_ACCOUNT" \
        --container-name "$CONTAINER_NAME" \
        --file "$FILE" \
        --name "$RELATIVE_PATH" \
        --auth-mode login \
        --overwrite true
done

echo "All files uploaded successfully!"
