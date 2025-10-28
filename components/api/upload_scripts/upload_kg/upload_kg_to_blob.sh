#!/bin/bash

# Check if the user provided the KG_NAME as an argument
if [ -z "$1" ]; then
    echo "Usage: $0 <KG_NAME>"
    exit 1
fi

# Define variables
CONTAINER_NAME="knowledge-graphs"
STORAGE_ACCOUNT="wegwijsdevstorage"
SOURCE_DIR="$PWD/knowledge-graphs"
KG_NAME="$1"

# Specify the file to be uploaded
FILE="$SOURCE_DIR/$KG_NAME"

# Check if the file exists
if [ -f "$FILE" ]; then
    echo "Uploading $FILE as $KG_NAME..."

    # Upload command
    az storage blob upload \
        --account-name "$STORAGE_ACCOUNT" \
        --container-name "$CONTAINER_NAME" \
        --file "$FILE" \
        --name "$KG_NAME" \
        --auth-mode login \
        --overwrite true

    echo "File uploaded successfully!"
else
    echo "File $FILE does not exist."
fi
