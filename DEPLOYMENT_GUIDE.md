# 🚀 Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8+
- ~15 minutes setup time

### Quick Setup

```bash
cd /home/ubuntu/Desktop/Project1

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env to add your API keys

# 3. Start all services
chmod +x run_all_services.sh
./run_all_services.sh

# 4. Access the system
# UI: http://localhost:8501
# API: http://localhost:8000/docs
```

## Docker Deployment

### Single Container (Dev/Test)

```bash
# Build image
docker build -t loan-approval-ai .

# Run specific service
docker run -p 8000:8000 loan-approval-ai python main.py
```

### Multi-Container Setup (Production Ready)

```bash
# Using docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Services

```yaml
Services:
- applicant-db:8001
- risk-rules:8002
- decision-synthesis:8003
- notification:8004
- api:8000
- streamlit:8501

Dependencies: Ordered startup, health checks enabled
```

## Cloud Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

```bash
# 1. Push image to ECR
aws ecr create-repository --repository-name loan-approval-ai
docker tag loan-approval-ai:latest {account}.dkr.ecr.{region}.amazonaws.com/loan-approval-ai:latest
docker push {account}.dkr.ecr.{region}.amazonaws.com/loan-approval-ai:latest

# 2. Create ECS Task Definition (task-definition.json)
# 3. Create ECS Service
# 4. Set up Load Balancer
# 5. Configure Auto Scaling
```

#### Using Elastic Beanstalk

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize project
eb init -p python-3.11 loan-approval-ai

# 3. Create environment
eb create loan-approval-prod

# 4. Deploy
eb deploy

# 5. Open in browser
eb open
```

### Kubernetes Deployment

#### Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loan-approval-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: loan-api
  template:
    metadata:
      labels:
        app: loan-api
    spec:
      containers:
      - name: api
        image: loan-approval-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic
        livenessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: loan-approval-svc
spec:
  selector:
    app: loan-api
  type: LoadBalancer
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

#### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace loan-approval

# Create secrets
kubectl create secret generic api-keys \
  --from-literal=anthropic=$ANTHROPIC_API_KEY \
  -n loan-approval

# Apply deployment
kubectl apply -f deployment.yaml -n loan-approval

# Check status
kubectl get pods -n loan-approval
kubectl get svc -n loan-approval

# View logs
kubectl logs -f deployment/loan-approval-api -n loan-approval
```

### GCP Deployment (Cloud Run)

```bash
# 1. Build and push to Container Registry
gcloud builds submit --tag gcr.io/{project}/loan-approval-ai

# 2. Deploy to Cloud Run
gcloud run deploy loan-approval-ai \
  --image gcr.io/{project}/loan-approval-ai \
  --platform managed \
  --region us-central1 \
  --set-env-vars ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  --allow-unauthenticated

# 3. Get service URL
gcloud run services describe loan-approval-ai
```

### Azure Deployment (App Service)

```bash
# 1. Create resource group
az group create --name loan-approval-rg --location eastus

# 2. Create App Service Plan
az appservice plan create \
  --name loan-approval-plan \
  --resource-group loan-approval-rg \
  --sku B2

# 3. Create Web App
az webapp create \
  --name loan-approval-app \
  --resource-group loan-approval-rg \
  --plan loan-approval-plan \
  --runtime "PYTHON|3.11"

# 4. Configure deployment
az webapp deployment source config-zip \
  --resource-group loan-approval-rg \
  --name loan-approval-app \
  --src app.zip
```

## Database Integration

### PostgreSQL Setup

```python
# Update config.py
DATABASE_URL = "postgresql://user:password@localhost/loan_approval"

# Update MCP servers
from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)

# Replace APPLICANT_DATABASE dict with:
def get_applicant(applicant_id):
    query = "SELECT * FROM applicants WHERE id = %s"
    result = db.execute(query, (applicant_id,))
    return result.fetchone()
```

### MongoDB Setup

```python
# For audit logs
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["loan_approval"]

async def log_decision(decision):
    db.decisions.insert_one({
        "case_id": decision["case_id"],
        "applicant_id": decision["applicant_id"],
        "timestamp": datetime.utcnow(),
        "result": decision
    })
```

## Monitoring & Logging

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server

# Metrics
applications_processed = Counter(
    'applications_processed_total',
    'Total applications processed'
)
approval_rate = Counter(
    'applications_approved_total',
    'Total approved applications'
)
processing_time = Histogram(
    'processing_time_seconds',
    'Application processing time'
)

# Start metrics server
start_http_server(8002)
```

### ELK Stack Integration

```python
import logging
from pythonjsonlogger import jsonlogger

# JSON logging for ELK
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# All logs will be JSON for easy parsing
```

### CloudWatch (AWS)

```python
import watchtower
import logging

# Send logs to CloudWatch
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        watchtower.CloudWatchLogHandler(),
    ]
)
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run tests
      run: python test_api.py
    
    - name: Build Docker image
      run: docker build -t loan-approval-ai:latest .
    
    - name: Push to Docker Hub
      run: |
        docker login -u ${{ secrets.DOCKER_USER }} -p ${{ secrets.DOCKER_PASS }}
        docker push loan-approval-ai:latest
    
    - name: Deploy to production
      run: kubectl set image deployment/loan-approval-api api=loan-approval-ai:latest
```

## Performance Optimization

### Caching Strategy

```python
from funcache import cache
import redis

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379)

@cache(redis_client, expire=3600)
async def get_applicant_profile(applicant_id):
    return await applicant_agent.analyze(applicant_id)
```

### Database Indexing

```sql
-- ApplicantDB indexes
CREATE INDEX idx_applicant_id ON applicants(applicant_id);
CREATE INDEX idx_credit_score ON applicants(credit_score);

-- Decision history indexes
CREATE INDEX idx_case_id ON decisions(case_id);
CREATE INDEX idx_timestamp ON decisions(created_at);
```

### Load Balancing

```nginx
# nginx.conf
upstream loan_api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    
    location /api {
        proxy_pass http://loan_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Hardening

### Environment Secrets

```bash
# Store sensitive data in environment variables
export ANTHROPIC_API_KEY=$(aws secretsmanager get-secret-value --secret-id anthropic-key --query SecretString --output text)

# Or use tools like:
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
```

### API Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthCredential

security = HTTPBearer()

@app.post("/api/submit-loan-application")
async def submit(
    application: LoanApplicationData,
    credentials: HTTPAuthCredential = Depends(security)
):
    if not verify_api_key(credentials.credentials):
        raise HTTPException(status_code=401)
    return await process(application)
```

### HTTPS/TLS

```bash
# Let's Encrypt certificate
certbot certonly --standalone -d loan-approval.example.com

# Use with FastAPI
uvicorn main:app --ssl-keyfile=/path/to/key.pem --ssl-certfile=/path/to/cert.pem
```

## Backup & Disaster Recovery

### Database Backups

```bash
# PostgreSQL backup
pg_dump -U user loan_approval > backup_$(date +%Y%m%d).sql

# MongoDB backup
mongodump --db loan_approval --archive=backup_$(date +%Y%m%d).archive

# Restore
psql -U user loan_approval < backup_20240701.sql
```

### S3 Backup

```bash
# Backup to AWS S3
aws s3 sync ./backups s3://loan-approval-backups/

# Restore from S3
aws s3 sync s3://loan-approval-backups/ ./backups
```

## Scaling Strategy

### Horizontal Scaling

```
Step 1: Start with 1-2 FastAPI instances
Step 2: Add load balancer (nginx/HAProxy)
Step 3: Add more API instances as needed
Step 4: Scale database (read replicas)
Step 5: Add caching layer (Redis)
Step 6: Consider multi-region deployment
```

### Performance Targets

```
Throughput: 100+ req/sec per instance
Latency: < 2 seconds p99
Availability: 99.9% uptime
Error Rate: < 0.1%
```

## Rollback Procedure

### Docker Rollback

```bash
# If deployment fails
docker-compose down
git revert <commit-hash>
docker-compose up -d
```

### Kubernetes Rollback

```bash
# View rollout history
kubectl rollout history deployment/loan-approval-api

# Rollback to previous version
kubectl rollout undo deployment/loan-approval-api

# Rollback to specific revision
kubectl rollout undo deployment/loan-approval-api --to-revision=5
```

## Monitoring Checklist

- [ ] Application logs aggregated (ELK/CloudWatch)
- [ ] Metrics collected (Prometheus)
- [ ] Alerts configured (PagerDuty/OpsGenie)
- [ ] Dashboards created (Grafana)
- [ ] Backups automated
- [ ] Disaster recovery tested
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Team trained on operation

---

**Ready to deploy! Follow the guide for your platform above.** 🚀
