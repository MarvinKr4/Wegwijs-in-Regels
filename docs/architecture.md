# Architecture Overview

## System Components

### Frontend

- Web interface for user interaction
- Communicates with backend services

### Backend Services

#### Law Storage (Elastic Search)

- Stores structured law information
- Indexes and searches through legal documents
- Handles full-text search capabilities

#### Knowledge Graph (Fuseki)

- Stores and manages semantic relationships
- Provides SPARQL endpoint for querying
- Maintains taxonomies and term definitions
- Links laws and law articles

#### Storage Backend

- Configurable storage solution
- Currently uses Azure Blob Storage
- Can be replaced with alternative solutions (S3, local storage, etc.)

### Data Sources

- Laws and regulations
- Case law
- Selectielijsten (Dutch archiving standards)
- Work instructions

## Data Flow

1. User interacts with the frontend interface
2. Frontend sends requests to backend services
3. Backend services:
   - Query Elastic Search for relevant laws
   - Access knowledge graph for context
   - Retrieve additional information from storage
4. Results are combined and returned to the user

## Deployment

The system can be deployed using:

- Local development environment (Docker Compose)
- Kubernetes cluster (Helm charts provided)
- Production deployment (configurable)

## Security

- GPG-based secret management
- Configurable authentication
- Secure storage of sensitive information

## Logging

- Application logs locally in the terminal when running `make develop`
- Tail pods running on remote cluster with `kubectl logs -f <pod-name>`

