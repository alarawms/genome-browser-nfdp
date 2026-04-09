# Docker Deployment Guide

> Containerized setup for Saudi Livestock Genome Browser
> Portable, reproducible, production-ready

**Created:** April 8, 2026

---

## 🐳 Overview

This project uses Docker Compose to orchestrate all services:

1. **Frontend:** JBrowse 2 (React)
2. **Backend:** FastAPI (Python)
3. **Database:** PostgreSQL
4. **Data Volume:** NAS-mounted genomes/QTLs

---

## 📁 Project Structure

```
sheep-qtl/
├── docker-compose.yml          # Main orchestration
├── Dockerfile.backend        # Backend container
├── Dockerfile.frontend       # Frontend container
├── docker/
│   ├── init-db.sql          # Database initialization
│   └── nginx.conf           # Reverse proxy config
├── src/
│   ├── backend/             # FastAPI code
│   ├── frontend/            # JBrowse 2 app
│   └── data-processing/     # Scripts
├── data/                    # Local data (mounted)
│   ├── genome/
│   ├── annotations/
│   ├── qtl/
│   └── comparative/
└── requirements-backend.txt   # Python dependencies
```

---

## 🐳 Docker Compose Configuration

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: saudi-livestock-db
    environment:
      POSTGRES_DB: saudi_livestock
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - saudi-livestock-network

  # FastAPI Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: saudi-livestock-backend
    environment:
      DATABASE_URL: postgresql://postgres:postgres@postgres:5432/saudi_livestock
      DATA_PATH: /app/data
      LOG_LEVEL: info
    volumes:
      - ./src/backend:/app/src
      - ./data:/app/data:ro          # Read-only access to genomes
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    networks:
      - saudi-livestock-network

  # JBrowse 2 Frontend
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: saudi-livestock-frontend
    environment:
      NODE_ENV: production
      API_BASE_URL: http://backend:8000
      JBROWSE_DATA_DIR: /app/data
    volumes:
      - ./src/frontend:/app
      - ./data:/app/data:ro          # Read-only access to genomes
    ports:
      - "8080:80"
    depends_on:
      - backend
    networks:
      - saudi-livestock-network

  # Nginx Reverse Proxy (Production)
  nginx:
    image: nginx:alpine
    container_name: saudi-livestock-nginx
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
    networks:
      - saudi-livestock-network

volumes:
  postgres_data:
    driver: local

networks:
  saudi-livestock-network:
    driver: bridge
```

---

## 🔧 Backend Dockerfile

### `Dockerfile.backend`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements-backend.txt .
RUN pip install --no-cache-dir -r requirements-backend.txt

# Copy application code
COPY src/backend /app/src
COPY docker/init-db.sql /docker-entrypoint-initdb.d/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔧 Frontend Dockerfile

### `Dockerfile.frontend`

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY src/frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY src/frontend/ .

# Build for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx config
COPY docker/nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1
```

---

## 📄 Python Dependencies

### `requirements-backend.txt`

```txt
# FastAPI and ASGI
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
psycopg2-binary==2.9.6
sqlalchemy==2.0.21
alembic==1.12.1

# Genome data processing
pysam==0.22.0
pyfaidx==0.7.2.1
biopython==1.83

# Data handling
pandas==2.1.4
numpy==1.26.2
openpyxl==3.1.2

# API utilities
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# HTTP client
httpx==0.25.0

# Logging
python-json-logger==2.0.7
```

---

## 📄 Database Initialization

### `docker/init-db.sql`

```sql
-- Saudi Livestock Genome Browser Database

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Species table
CREATE TABLE species (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(200),
    assembly VARCHAR(100),
    genome_size_gb NUMERIC,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- QTL table
CREATE TABLE qtls (
    id SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES species(id) ON DELETE CASCADE,
    chromosome VARCHAR(50) NOT NULL,
    start_pos INTEGER NOT NULL,
    end_pos INTEGER NOT NULL,
    trait VARCHAR(200),
    confidence NUMERIC,
    reference TEXT,
    pmid INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_qtls_species ON qtls(species_id);
CREATE INDEX idx_qtls_chromosome ON qtls(chromosome);
CREATE INDEX idx_qtls_trait ON qtls USING gin(trait gin_trgm_ops);

-- Traits table
CREATE TABLE traits (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL UNIQUE,
    category VARCHAR(100),
    saudi_relevance BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Saudi breeds table
CREATE TABLE saudi_breeds (
    id SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES species(id) ON DELETE CASCADE,
    breed_name VARCHAR(200) NOT NULL,
    arabian_name TEXT,
    region VARCHAR(100),
    population_size INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial species
INSERT INTO species (name, scientific_name, assembly, genome_size_gb) VALUES
    ('Sheep', 'Ovis aries', 'Oar_rambouillet_v1.0', 2.7),
    ('Camel', 'Camelus dromedarius', 'CamDro2', 2.5),
    ('Cattle', 'Bos taurus', 'ARS-UCD1.2', 2.7),
    ('Goat', 'Capra hircus', 'CHIR_1.0', 2.7),
    ('Horse', 'Equus caballus', 'EquCab3.0', 2.7);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
```

---

## 🚀 Quick Start Commands

### Build and Start

```bash
# Navigate to project directory
cd /home/sanad/ai-workspace/sheep-qtl

# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Development Mode

```bash
# Start with hot reload for backend
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production Mode

```bash
# Start with production optimization
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 🔌 Nginx Configuration

### `docker/nginx.conf`

```nginx
events {
    worker_connections 1024;
}

http {
    upstream frontend {
        server frontend:80;
    }

    upstream backend {
        server backend:8000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
    limit_req_status 429;

    server {
        listen 80;
        server_name saudi-livestock.local;

        # Client max body size (for file uploads)
        client_max_body_size 100M;

        # Frontend (JBrowse 2 static files)
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;

            # CORS headers
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;

            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy";
        }

        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    }
}
```

---

## 📊 Data Volume Management

### Local Development

```bash
# Create data directory structure
mkdir -p data/{genome,annotations,qtl,comparative}

# Download genomes to data/ (mounted into containers)
# QTL data goes to data/qtl/
# Annotations go to data/annotations/
```

### Production on kw61001

```bash
# Mount NAS volumes
docker-compose up -d

# Data mounted from:
# /home/sanad/ai-workspace/sheep-qtl/data -> /app/data
# NAS path: nas:AI-workspace/sheep-qtl/data
```

---

## 🔒 Security Considerations

### Environment Variables

```bash
# Create .env file (git ignored)
cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/saudi_livestock
POSTGRES_PASSWORD=your_secure_password_here
JWT_SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://localhost:8080
EOF
```

### Docker Secrets

```bash
# Use Docker secrets for production
echo "your_password" | docker secret create saudi_livestock_db_password -
```

---

## 📈 Scaling Options

### Horizontal Scaling (Frontend)

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  frontend:
    deploy:
        replicas: 3  # 3 frontend instances
```

### Vertical Scaling (Backend)

```bash
# Allocate more resources
docker-compose up -d --scale backend=1
docker update --cpus=4 --memory=4g backend
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres

# Check container status
docker-compose ps

# Rebuild containers
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Test PostgreSQL connection
docker-compose exec postgres psql -U postgres -d saudi_livestock

# Check if database is ready
docker-compose exec postgres pg_isready -U postgres
```

### Port Conflicts

```yaml
# Change ports in docker-compose.yml
services:
  backend:
    ports:
      - "8001:8000"  # Changed from 8000
  frontend:
    ports:
      - "8081:80"  # Changed from 8080
```

---

## 📦 Building Images

```bash
# Build backend image
docker build -f Dockerfile.backend -t saudi-livestock-backend .

# Build frontend image
docker build -f Dockerfile.frontend -t saudi-livestock-frontend .

# Push to registry (optional)
docker push saudi-livestock-backend:latest
docker push saudi-livestock-frontend:latest
```

---

## 🌐 Accessing the Application

### Local Development
- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **Database:** localhost:5432

### Production on kw61001 (Tailscale)
- **Application:** http://kw61001.something
- **Tailscale URL:** http://kw61001:80/sheep-qtl
- **HTTPS:** Configure SSL certificates in nginx

---

## 📝 Production Deployment Steps

### 1. Prepare Environment

```bash
# SSH into kw61001
ssh kw61001

# Clone or copy project
cd /home/sanad/ai-workspace/sheep-qtl

# Create production .env
cp .env.example .env
# Edit .env with production values
nano .env
```

### 2. Deploy

```bash
# Build and start in detached mode
docker-compose -f docker-compose.prod.yml up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. SSL/TLS Configuration

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem

# Or use Let's Encrypt for production
certbot certonly --standalone -d yourdomain.com
```

---

## 🔄 Continuous Deployment

### GitHub Actions (Optional)

```yaml
# .github/workflows/deploy.yml
name: Deploy to kw61001

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to kw61001
        run: |
          docker-compose -H ssh://user@kw61001 up -d
```

---

## 📊 Monitoring

### Container Health

```bash
# Check all services
docker-compose ps

# Specific service health
docker-compose exec backend curl -f http://localhost:8000/health
docker-compose exec frontend wget -q http://localhost:80/health
```

### Log Management

```bash
# View logs
docker-compose logs --tail=100

# Export logs
docker-compose logs > logs.txt

# Configure log rotation (in docker-compose.yml)
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 📚 Documentation Links

- **Docker Compose:** https://docs.docker.com/compose/
- **Dockerfile Reference:** https://docs.docker.com/engine/reference/builder/
- **Nginx Documentation:** https://nginx.org/en/docs/
- **PostgreSQL in Docker:** https://hub.docker.com/_/postgres/

---

**Last Updated:** April 8, 2026
**Next:** Create Docker files and test local deployment

---

*Containerized deployment guide created*
