# INSTALLATION AND DEPLOYMENT GUIDE

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Local Installation](#local-installation)
3. [Running Tests](#running-tests)
4. [Starting the API](#starting-the-api)
5. [Running Scraper](#running-scraper)
6. [Docker Installation](#docker-installation)
7. [Ubuntu Server Deployment](#ubuntu-server-deployment)
8. [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Specifications
- **CPU**: 2 cores
- **RAM**: 2GB
- **Disk**: 1GB free space
- **Python**: 3.10 or higher
- **OS**: Windows, macOS, or Linux

### Recommended for Production
- **CPU**: 4+ cores
- **RAM**: 8GB
- **Disk**: 2GB free space
- **Database**: SQLite (built-in) or PostgreSQL (optional)

---

## Local Installation

### Windows

#### Step 1: Install Python 3.10+
1. Download from https://www.python.org/downloads/
2. During installation, **check "Add Python to PATH"**
3. Open PowerShell and verify:
   ```powershell
   python --version
   ```

#### Step 2: Clone/Extract Project
```powershell
cd C:\Users\YourUsername\Documents
git clone https://github.com/your-repo/ghana-legal-scraper.git
cd ghana-legal-scraper
```

#### Step 3: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Step 4: Install Dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 5: Verify Installation
```powershell
python quickstart.py
```

### macOS

#### Step 1: Install Python 3.10+
Using Homebrew:
```bash
brew install python@3.10
```

#### Step 2-5: Same as Linux (see below)

### Linux (Ubuntu/Debian)

#### Step 1: Install Python 3.10+
```bash
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip git
```

#### Step 2: Clone Project
```bash
cd ~/Documents
git clone https://github.com/your-repo/ghana-legal-scraper.git
cd ghana-legal-scraper
```

#### Step 3: Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 5: Verify Installation
```bash
python quickstart.py
```

---

## Running Tests

### Run All Tests
```bash
python main.py test
```

### Expected Output
```
test_sample_case_1_republic_v_highcourt PASSED
test_sample_case_2_akufo_addo_v_electoral PASSED
test_sample_case_3_margaret_banful PASSED
test_extract_judges PASSED
test_parse_date_formats PASSED
test_validate_case_citation_format PASSED

============================== 6 passed in 0.85s ===============================
```

### Run Specific Test
```bash
pytest tests/test_scraper.py::TestValidator::test_parse_date_formats -v
```

### Generate Coverage Report
```bash
pytest tests/ --cov=scraper --cov=api --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Starting the API

### Basic Usage
```bash
# Ensure venv is activated
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\Activate.ps1  # Windows

# Start API on localhost:8000
python main.py api
```

### Custom Configuration
```bash
# Different port
python main.py api --port 8080

# Custom host (for network access)
python main.py api --host 0.0.0.0 --port 8000

# With auto-reload (development)
python main.py api --reload
```

### Accessing API
1. **Interactive Documentation**: http://localhost:8000/docs
2. **Alternative Documentation**: http://localhost:8000/redoc
3. **API Root**: http://localhost:8000/

### API Endpoints Quick Reference

```bash
# Basic search
curl "http://localhost:8000/search?q=property"

# Advanced search
curl "http://localhost:8000/search/advanced?year_from=2020&statute=Act%2029"

# Get case by ID
curl "http://localhost:8000/case/GHASC/2023/45"

# Statistics
curl "http://localhost:8000/stats"

# Health check
curl "http://localhost:8000/health"
```

---

## Running Scraper

### Test Mode (Recommended First)
```bash
python main.py scrape --test
```
- Scrapes only 10 cases
- Takes ~5 minutes
- Useful for validation

### Full Campaign
```bash
python main.py scrape
```
- Scrapes 500+ cases
- Takes 2-3 hours
- Can be interrupted with Ctrl+C

### Monitoring Progress

While scraping, check:
- **Daily stats**: `data/stats/YYYY-MM-DD_stats.json`
- **Error log**: `data/logs/errors.log`
- **Quality report**: `data/logs/quality_report.log`

---

## Docker Installation

### Prerequisites
- Docker installed (https://www.docker.com/products/docker-desktop)
- Docker Compose (included with Docker Desktop)

### Build and Run

```bash
# Build image
docker build -t ghana-legal-scraper .

# Run API container
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  ghana-legal-scraper

# Or use Docker Compose
docker-compose up -d
```

### Access API in Docker
```bash
curl http://localhost:8000/docs
```

### View Container Logs
```bash
docker logs -f ghana-legal-scraper-api
```

### Stop Container
```bash
docker-compose down
```

### Run Scraper in Docker
```bash
docker run -it \
  -v $(pwd)/data:/app/data \
  ghana-legal-scraper \
  python main.py scrape --test
```

---

## Ubuntu Server Deployment

### Automated Deployment (Recommended)

```bash
# Make script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

The script will:
1. Install Python dependencies
2. Create Python virtual environment
3. Setup systemd service
4. Start the service

### Manual Deployment

#### Step 1: Install System Dependencies
```bash
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3-pip \
  libxml2 libxslt1.1 nginx supervisor
```

#### Step 2: Create Application User
```bash
sudo useradd -m -s /bin/bash -d /opt/ghana-legal-scraper glis
```

#### Step 3: Clone and Setup
```bash
cd /opt/ghana-legal-scraper
sudo chown -R glis:glis .

# Switch to glis user
sudo su - glis

# Setup venv
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Step 4: Create Systemd Service
```bash
sudo nano /etc/systemd/system/glis-api.service
```

Add this content:
```ini
[Unit]
Description=Ghana Legal Scraper API
After=network.target

[Service]
Type=simple
User=glis
WorkingDirectory=/opt/ghana-legal-scraper
ExecStart=/opt/ghana-legal-scraper/venv/bin/python main.py api --host 0.0.0.0
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

#### Step 5: Enable and Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable glis-api
sudo systemctl start glis-api
sudo systemctl status glis-api
```

#### Step 6: Setup Nginx Reverse Proxy
```bash
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 7: Access API
```
http://your-server-ip:8000/docs
```

### Service Management

```bash
# Check status
sudo systemctl status glis-api

# View logs
sudo journalctl -u glis-api -f

# Restart service
sudo systemctl restart glis-api

# Stop service
sudo systemctl stop glis-api
```

---

## SSL/TLS Certificate Setup (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d glis.gh -d www.glis.gh

# Update nginx.conf with certificate paths
sudo nano /etc/nginx/nginx.conf
# Uncomment SSL certificate lines and set paths

# Restart nginx
sudo systemctl restart nginx

# Auto-renew certificates (cron job)
sudo certbot renew --dry-run
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'scraper'"

**Cause**: Python path not set correctly
**Solution**:
```bash
# Ensure you're in project root
cd /path/to/ghana-legal-scraper

# Activate venv
source venv/bin/activate

# Run again
python main.py test
```

### Issue: "Database is locked"

**Cause**: Multiple processes accessing database simultaneously
**Solution**:
```bash
# Kill all Python processes
pkill -f "python main.py"

# Wait a moment, then restart
python main.py api
```

### Issue: "Connection refused" on API

**Cause**: Port already in use
**Solution**:
```bash
# Check which process is using port 8000
lsof -i :8000

# Use different port
python main.py api --port 8001
```

### Issue: ImportError with requests/beautifulsoup

**Cause**: Virtual environment not activated
**Solution**:
```bash
# Activate venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\Activate.ps1  # Windows

# Reinstall
pip install -r requirements.txt
```

### Issue: "Permission denied" on Linux

**Cause**: Incorrect file permissions
**Solution**:
```bash
sudo chown -R $USER:$USER .
chmod -x data/
chmod -x venv/
```

### Issue: Scraper runs slowly

**Cause**: Rate limiting or network issues
**Solution**:
1. Check internet connection
2. Verify GhanaLII is accessible: `curl https://ghalii.org`
3. Check `data/logs/errors.log` for failed requests

### Issue: Low quality scores

**Cause**: Missing data fields or validation failures
**Solution**:
```bash
# View validation errors
tail -f data/logs/errors.log

# Check quality report
cat data/stats/$(date +%Y-%m-%d)_report.json
```

### Issue: Out of memory during scraping

**Cause**: Too many cases processed at once
**Solution**:
```bash
# Reduce batch size or use smaller year ranges
# Edit config/settings.py and restart
```

---

## Performance Tuning

### For Production

Edit `config/settings.py`:

```python
# Increase database performance
DATABASE_PATH = '/ssd/path/to/database.db'  # Use SSD if possible

# Adjust rate limiting if needed (with caution)
REQUEST_DELAY = 3  # Minimum 2 seconds for safe scraping

# API performance
API_WORKERS = 4  # Use: gunicorn -w 4
```

### Run with Gunicorn (Production)

```bash
pip install gunicorn

# Start with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 api.main:app

# With reload on code changes
gunicorn -w 4 -b 0.0.0.0:8000 --reload api.main:app
```

---

## Backup Strategy

### Backup Database
```bash
# Backup SQLite database
cp data/processed/ghasc_cases.db backups/ghasc_cases_backup_$(date +%Y%m%d).db

# Backup JSON
cp data/processed/cases.json backups/cases_backup_$(date +%Y%m%d).json

# Create automated backup (cron)
0 2 * * * /opt/ghana-legal-scraper/backup.sh
```

### Backup Script
```bash
#!/bin/bash
BACKUP_DIR="/backups/glis"
mkdir -p $BACKUP_DIR
cp /opt/ghana-legal-scraper/data/processed/* $BACKUP_DIR/
echo "Backup completed: $(date)" >> $BACKUP_DIR/backup.log
```

---

## Security Considerations

1. **API Authentication**: Consider adding API key validation for production
2. **Rate Limiting**: Already implemented (1 req/5 sec)
3. **Data Privacy**: Ensure compliance with data protection laws
4. **HTTPS**: Always use HTTPS in production (Let's Encrypt)
5. **Firewall**: Restrict access to API to trusted IPs

---

## Support

For issues:
1. Check logs: `data/logs/`
2. Run tests: `python main.py test`
3. Review README.md
4. Check API docs: http://localhost:8000/docs

---

**Status**: Production Ready  
**Version**: 1.0.0  
**Last Updated**: January 6, 2024
