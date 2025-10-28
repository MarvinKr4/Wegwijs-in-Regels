#!/bin/bash

# Define variables
CONTAINER_NAME="legal-docs"
STORAGE_ACCOUNT="wegwijsdevstorage"
SOURCE_DIR="$PWD/laws/articles"

# Upload files recursively
find "$SOURCE_DIR" -type f | while read -r FILE; do
    # Generate relative path for blob name
    RELATIVE_PATH=${FILE#"$SOURCE_DIR/"}

    echo "Uploading $FILE as $RELATIVE_PATH..."

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
