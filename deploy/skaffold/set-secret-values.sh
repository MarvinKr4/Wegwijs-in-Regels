#!/bin/bash
set -e

export GPT_API_KEY=$(pass wegwijs-credentials/GPT_TOKEN_1)
export GPT_EMBEDDINGS_KEY=$(pass wegwijs-credentials/GPT4_TOKEN_1)
export AZURE_STORAGE_CONNECTION_STRING=$(pass wegwijs-credentials/BLOB_STORAGE_CONNECTION_STRING)

# ...add all necessary environment variables if using GPG / Pass

yq '
    .api.llm.gpt.apiKey = strenv(GPT_API_KEY) |
    .api.llm.gpt.embeddingsKey = strenv(GPT_EMBEDDINGS_KEY) |
    .api.storage.storgeAccountConnectionString = strenv(AZURE_STORAGE_CONNECTION_STRING)
' secret-values-template.yaml > secret-values.yaml
