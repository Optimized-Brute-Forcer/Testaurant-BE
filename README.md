# Testaurant Backend

An automated testing platform for backend services with multi-organization RBAC support.

## Features

- 🔐 **Multi-Organization RBAC**: Secure isolation with role-based access control
- 🚀 **Multi-Protocol Testing**: REST APIs, SQL databases, and MongoDB
- 🔗 **Data Feed-Forward**: Chain test steps with dynamic data passing
- ✅ **Response Validation**: Automated validation against expected responses
- 📊 **Execution History**: Comprehensive audit logs and execution tracking
- 🌍 **Environment Management**: Support for multiple environments (QA, PREPROD, PROD)

## Architecture

- **Backend**: FastAPI (Python 3.11+) with MongoDB and SQLAlchemy
- **Authentication**: Google OAuth 2.0 + JWT
- **Database**: MongoDB (application data), MySQL/PostgreSQL (test targets)

## Quick Start

### Prerequisites

- Python 3.11+
- MongoDB
- Git

### Local Development

```bash
# Clone the repository
git clone <repository-url>
cd Testaurant-BE

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
nano .env  # Edit with your configuration

# Run the application
uvicorn app.main:app --reload --port 8080
```

Visit `http://localhost:8080/docs` to access the API documentation.

## EC2 Deployment (AWS Free Tier)

### Step 1: Launch EC2 Instance

1. Launch an **Ubuntu 22.04 LTS** t2.micro instance (free tier eligible)
2. Configure security group to allow:
   - SSH (port 22) from your IP
   - HTTP (port 80) from anywhere
   - Custom TCP (port 8080) from anywhere
3. Create or use existing key pair for SSH access

### Step 2: Connect to EC2

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 3: Install Python 3.11

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev git
```

### Step 4: Clone and Deploy

```bash
# Clone repository
git clone <repository-url>
cd Testaurant-BE

# Run deployment script
bash deploy.sh
```

### Step 5: Configure Environment Variables

```bash
# Edit .env file with your configuration
nano .env
```

Required environment variables:
- `MONGODB_URL`: MongoDB connection string
- `JWT_SECRET`: Secret key for JWT tokens
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret

### Step 6: Run as Background Service

```bash
# Set up systemd service
sudo bash setup_service.sh

# Check service status
sudo systemctl status testaurant

# View logs
sudo journalctl -u testaurant -f
```

### Step 7: Access the API

Your API will be available at:
- `http://your-ec2-public-ip:8080`
- API docs: `http://your-ec2-public-ip:8080/docs`

### Optional: Set Up Nginx Reverse Proxy

```bash
# Install nginx
sudo apt install -y nginx

# Create nginx configuration
sudo nano /etc/nginx/sites-available/testaurant
```

Add the following configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # or your EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/testaurant /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Optional: Set Up SSL with Let's Encrypt

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (requires a domain name)
sudo certbot --nginx -d your-domain.com
```

## Project Structure

```
Testaurant-BE/
├── app/                    # FastAPI application
│   ├── controllers/        # API endpoints
│   ├── models/             # Pydantic models
│   ├── services/           # Business logic
│   ├── middleware/         # RBAC middleware
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Configuration
│   └── database.py         # Database connections
├── deploy.sh               # EC2 deployment script
├── setup_service.sh        # Systemd service setup
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Development

### Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests (when available)
pytest
```

### API Documentation

Once the application is running, visit:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

## Troubleshooting

### Service won't start

```bash
# Check service logs
sudo journalctl -u testaurant -n 50

# Check if port 8080 is in use
sudo lsof -i :8080

# Restart service
sudo systemctl restart testaurant
```

### MongoDB connection issues

- Verify `MONGODB_URL` in `.env` is correct
- Ensure MongoDB is accessible from EC2 instance
- Check security group rules if using MongoDB Atlas

### Permission errors

```bash
# Ensure correct ownership
sudo chown -R ubuntu:ubuntu /path/to/Testaurant-BE
```

## License

MIT
