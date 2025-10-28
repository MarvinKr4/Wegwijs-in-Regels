#!/bin/bash

# Define variables
CONTAINER_NAME="knowledge-graphs"
STORAGE_ACCOUNT="wegwijsdevstorage"
SOURCE_DIR="/home/$USER/repos/knowledge-graphs"
KG_NAME="Taxonomy.ttl"

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
