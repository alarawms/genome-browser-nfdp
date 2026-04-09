# Quick Start: Docker Deployment

> Build and run containerized Saudi Livestock Genome Browser

**Last Updated:** April 8, 2026

---

## 🚀 One-Command Start

```bash
# Navigate to project directory
cd /home/sanad/ai-workspace/sheep-qtl

# Build and start all services
docker-compose up -d
```

That's it! 🎉

The application will be available at:
- **Frontend:** http://localhost:8080
- **Backend API:** http://localhost:8000
- **Database:** localhost:5432

---

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 4GB RAM (8GB recommended)
- 16GB free disk space

---

## 🔧 Setup Steps

### 1. Clone/Access Project

```bash
# If cloning
git clone <repository-url> sheep-qtl
cd sheep-qtl

# Or navigate to existing project
cd /home/sanad/ai-workspace/sheep-qtl
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your settings
nano .env
```

**Important:** Change `JWT_SECRET_KEY` in production!

### 3. Prepare Data Directory

```bash
# Create data directory structure
mkdir -p data/{genome,annotations,qtl,comparative}

# Download genomes to data/ (optional, can do later)
# QTL data will go to data/qtl/
# Annotations go to data/annotations/
```

### 4. Build and Start

```bash
# Build and start all services
docker-compose up -d

# Check services are running
docker-compose ps

# View logs
docker-compose logs -f
```

---

## 🐳 Services

### PostgreSQL Database
- **Container Name:** saudi-livestock-db
- **Port:** 5432
- **Volume:** postgres_data (persisted)
- **Health:** Auto-healing enabled

### FastAPI Backend
- **Container Name:** saudi-livestock-backend
- **Port:** 8000
- **Dependencies:** PostgreSQL (waits for healthy)
- **Health Check:** http://localhost:8000/health

### JBrowse 2 Frontend
- **Container Name:** saudi-livestock-frontend
- **Port:** 8080
- **Dependencies:** Backend (API)
- **Data:** Mounted read-only from data/

---

## 📊 Service Status

```bash
# Check all services
docker-compose ps

# Specific service status
docker-compose ps postgres
docker-compose ps backend
docker-compose ps frontend

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

---

## 🛠 Troubleshooting

### Issue: Containers won't start

```bash
# View logs to see error
docker-compose logs

# Rebuild containers
docker-compose up -d --build

# Check port conflicts
docker-compose ps
lsof -i :8080
lsof -i :8000
lsof -i :5432
```

### Issue: Database connection fails

```bash
# Check database is healthy
docker-compose exec postgres pg_isready -U postgres

# Test connection
docker-compose exec backend python -c "from src.database import engine; print(engine.connect())"
```

### Issue: Frontend can't reach backend

```bash
# Check backend is running
docker-compose ps backend

# Test backend health
curl http://localhost:8000/health

# Check network connectivity
docker-compose exec frontend ping backend
```

### Issue: Need to rebuild after code changes

```bash
# Stop and rebuild
docker-compose down
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

---

## 🚀 Production Deployment (kw61001)

### 1. Prepare Environment

```bash
# SSH into kw61001
ssh kw61001

# Navigate to project
cd /home/sanad/ai-workspace/sheep-qtl

# Copy and configure .env
cp .env.example .env
nano .env
```

### 2. Deploy

```bash
# Build and start in detached mode
docker-compose up -d

# Check services
docker-compose ps

# View logs
docker-compose logs -f
```

### 3. Configure SSL/TLS (Optional)

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/key.pem \
  -out /etc/nginx/ssl/cert.pem

# Or use Let's Encrypt for production
# Configure nginx to use SSL
```

### 4. Accessing from Tailscale

```bash
# Access via Tailscale URL
# http://kw61001.something:8080/sheep-qtl

# Or configure DNS
```

---

## 🔄 Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data!)
docker-compose down -v

# Stop specific service
docker-compose stop backend
docker-compose stop frontend
```

---

## 📈 Scaling

### Scale Frontend (Horizontal)

```bash
# Run multiple frontend instances
docker-compose up -d --scale frontend=3
```

### Allocate More Resources (Vertical)

```bash
# Docker Desktop: Configure in settings
# Linux: Use Docker runtime flags
docker-compose up -d
docker update --cpus=4 --memory=4g backend
docker update --cpus=2 --memory=2g frontend
```

---

## 📝 Development Workflow

### Hot Reload Backend

```bash
# Start with auto-reload
docker-compose up backend

# Changes to src/backend/ will trigger rebuild
# Useful during development
```

### Mount Local Source

```bash
# Current setup already mounts source code
# Edit src/backend/ files locally
# Changes reflected immediately
```

---

## 🐳 Docker Commands Reference

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs

# Restart service
docker-compose restart backend

# Remove containers
docker-compose rm -f

# Remove volumes (CAUTION!)
docker-compose down -v

# Force rebuild
docker-compose up -d --build

# Scale services
docker-compose up -d --scale frontend=3
```

---

## 📊 Resource Requirements

### Minimum (Development)
- **CPU:** 2 cores
- **RAM:** 4GB
- **Disk:** 16GB

### Recommended (Production)
- **CPU:** 4+ cores
- **RAM:** 8-16GB
- **Disk:** 20-30GB (for all genomes)

---

## 🔒 Security Best Practices

1. **Change default passwords** in production
2. **Use secrets management** (Docker secrets, Vault, etc.)
3. **Enable HTTPS/TLS** in production
4. **Network isolation** (use custom network)
5. **Regular updates** (`docker-compose pull`)

---

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **PostgreSQL in Docker:** https://hub.docker.com/_/postgres/

---

**Quick Start Created:** April 8, 2026
**One-command deployment ready:** `docker-compose up -d` 🚀
