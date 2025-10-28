# Installation Guide

## Prerequisites

### System Requirements

- Linux/macOS/Windows with WSL2
- Docker and Docker Compose
- Kubernetes (for production deployment)
- GPG for secret management
- Python 3.12 or higher
- Node.js 16 or higher (for frontend development)

#### Development

- Skaffold
- KIND
- Pass (if using)
- k9s (optional, for viewing cluster)

### Required Accounts and Services

- GitHub account (for code access)
- Docker Hub account (for container images)
- Storage solution (Azure Blob Storage, S3, or local storage)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/wegwijs.git
cd wegwijs
```

### 2. Development Environment setup

#### Python Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Helm Dependencies

To install the required Helm chart dependencies, run:

```bash
cd deploy/helm
helm dependency build
```

#### Frontend Setup

```bash
cd components/frontend
npm install
```

### 3. Environment values

The application uses several environment values for secrets, endpoints, etc. These environment values need to be set in your environment. See `/deploy/helm/templates` for the values used.

We used GPG & Pass (linux) for secret management and sharing. See `set-secret-values.sh` for examples how to ingest secrets using Pass.

> `set-secret-values` is called when running `make develop`. When injecting environment values differently, you need to change this script.

### 4. Configuration

Configuration for the application is defined in `deploy/helm/values.yaml`

Using Skaffold for local development you can overwrite this configuration using `deploy/helm/skaffold/values.yaml`.

**Configure ElasticSearch**
The indices are created when ingesting the documents (law and case law), see step 6 below.

**Configure postgres**
Use alembic to set up the defined tables.

```bash
# Running this imports the sqlalchemy models define, connects to the db and check if they are there, and generates a revision script that prepares to update the db based on the defined models 
alembic revision --autogenerate -m "Create tables"   

# To actually execute it, run: 
alembic upgrade head 
```

### 5. Start the Development Environment

```bash
# Update Helm dependencies
make helm-dependency-update

# Start the development environment
make develop
```

### 6. Ingest data

The data sources either needs to be scraped (for laws and case laws) or exists already in the repo.
All sources are uploaded to blob before ingestion into the application. Scripts for uploading to blob can be found in the folder `components/api/upload_scripts`

*NOTE: for uploading, portfortward the api-component to port 5000 (default)

**Laws and case laws**
For laws and case laws scraping is required. The scripts for scraping are in the folder `components/api/scrapers`.
There is a python script each for case law and laws and additionally make command in the Makefile to run the scraping. Upload to blob and then ingest (and vectorize) the law documents into ElasticSearch by running:
`make ingest-es` - for laws
`make ingest-case-law` - for case laws

**Werkinstructies**
The werkinstructies exist in the folder `components/api/scrapers/werkinstructies`
The werkinstructies also needs to be uploaded to blob and then ingested with `make ingest-werk-instructie`

**Knowledge graphs**
All knowledge graphs are available in the repo in the folder `components/api/knowledge-graphs`.
They need to be uploaded to blob and then ingested with `make ingest-graphs`

**Selectielijsten**
The selectielijsten CSV-file for the Waterschap is in the folder `components/api/scrapers/selectielijsten/csv`.
Upload to blob and run `make ingest-selectielijsten`


If everything is already in blob you can also run `make ingest-all` to ingest all sources at once

### 7. Verify Installation

1. Check if all services are running:

   ```bash
   make k9s
   ```

2. Port-forward the frontend pod and access the application: http://localhost:3000

## Troubleshooting

### Common Issues

1. **Port conflicts**

   - Check if ports 3000 and 7861 are available
   - Modify port mappings in docker-compose.yml if needed

2. **Storage backend connection**
   - Verify credentials and connection strings
   - Check network connectivity to storage service
