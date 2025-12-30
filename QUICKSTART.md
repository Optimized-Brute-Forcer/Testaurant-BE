# Testaurant - Quick Start Guide

## 🚀 How to Run This Project

### Prerequisites

Before you start, make sure you have:
- **Python 3.11+** installed
- **Node.js 18+** installed
- **MongoDB** running locally or accessible remotely
- **Google OAuth credentials** (see setup below)

---

## Option 1: Local Development (Recommended for Development)

### Step 1: Get Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google+ API**
4. Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Add authorized redirect URIs:
   - `http://localhost:5173`
   - `http://localhost:3000`
7. Copy your **Client ID** and **Client Secret**

### Step 2: Start MongoDB

```bash
# macOS (with Homebrew)
brew services start mongodb-community

# Linux
sudo systemctl start mongod

# Windows
net start MongoDB

# Or use Docker
docker run -d -p 27017:27017 --name testaurant-mongo mongo:7
```

### Step 3: Setup Backend

```bash
# Navigate to backend directory
cd testaurant_bff

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Generate a secure JWT secret key (optional but recommended):
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Start the backend server
uvicorn app.main:app --reload --port 8080
```

**Backend will be running at:** `http://localhost:8080`
**API Documentation:** `http://localhost:8080/docs`

### Step 4: Setup Frontend

Open a **new terminal** and run:

```bash
# Navigate to frontend directory
cd testaurant_ui

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Edit .env and add your Google Client ID:
# VITE_GOOGLE_CLIENT_ID=your-google-client-id-here
# VITE_API_BASE_URL=http://localhost:8080

# Start the frontend dev server
npm run dev
```

**Frontend will be running at:** `http://localhost:5173`

### Step 5: Access the Application

1. Open your browser and go to `http://localhost:5173`
2. Click "Continue with Google"
3. Sign in with your Google account
4. You'll be redirected to the dashboard
5. Click "Create Organization" to set up your testing organization

---

## Option 2: Docker (Recommended for Production)

### Step 1: Configure Environment

```bash
# Copy Docker environment template
cp .env.docker .env

# Edit .env and add your Google OAuth credentials:
# JWT_SECRET_KEY=your-secret-key-here
# GOOGLE_CLIENT_ID=your-google-client-id
# GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Step 2: Build and Run with Docker Compose

```bash
# Build and start all services (MongoDB, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

**Services:**
- **Frontend:** `http://localhost:80`
- **Backend API:** `http://localhost:8080`
- **API Docs:** `http://localhost:8080/docs`
- **MongoDB:** `localhost:27017`

---

## 🔧 Troubleshooting

### Backend won't start

**Issue:** MongoDB connection error
```bash
# Check if MongoDB is running
mongosh

# If not running, start it:
brew services start mongodb-community  # macOS
sudo systemctl start mongod            # Linux
```

**Issue:** Module not found
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**Issue:** Port 8080 already in use
```bash
# Find and kill the process using port 8080
lsof -ti:8080 | xargs kill -9  # macOS/Linux

# Or change the port in .env:
PORT=8081
```

### Frontend won't start

**Issue:** Node modules not found
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Issue:** Port 5173 already in use
```bash
# Vite will automatically use the next available port
# Or kill the process:
lsof -ti:5173 | xargs kill -9  # macOS/Linux
```

**Issue:** Google OAuth fails
- Verify your Google Client ID is correct in `.env`
- Check that `http://localhost:5173` is in your authorized redirect URIs
- Clear browser cookies and try again

### Docker issues

**Issue:** Docker containers won't start
```bash
# Check Docker is running
docker ps

# View container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Rebuild containers
docker-compose build --no-cache
docker-compose up -d
```

---

## 📝 Next Steps After Running

1. **Create an Organization:**
   - Click "Create Organization" on the dashboard
   - Fill in organization details
   - Add teams (optional)
   - Add database credentials for testing (optional)

2. **Explore the API:**
   - Visit `http://localhost:8080/docs` for interactive API documentation
   - Test endpoints directly from the Swagger UI

3. **Start Testing:**
   - Create workitems for REST APIs, SQL, or MongoDB
   - Group workitems into testcases
   - Execute tests and view results

---

## 🎯 What's Working Now

✅ **Authentication:**
- Google OAuth login
- JWT token management
- Organization creation

✅ **Organization Management:**
- Create organizations with admin role
- Add teams with managers and developers
- Store database credentials for testing

✅ **UI:**
- Modern dashboard
- Organization setup wizard
- Responsive design

---

## 🚧 What's Next (To Be Implemented)

The following features are planned but not yet implemented:

- [ ] Workitem CRUD operations
- [ ] Testcase CRUD operations
- [ ] Testsuite CRUD operations
- [ ] Test execution engine
- [ ] Feed-forward mechanism
- [ ] Response validation

---

## 📚 Additional Resources

- **Setup Guide:** See `setup_guide.md` for detailed setup instructions
- **Implementation Plan:** See `implementation_plan.md` for architecture details
- **Walkthrough:** See `walkthrough.md` for what's been implemented

---

## 🆘 Need Help?

If you encounter any issues:

1. Check the logs:
   - Backend: Terminal where `uvicorn` is running
   - Frontend: Browser console (F12)
   - Docker: `docker-compose logs -f`

2. Verify environment variables:
   - Backend: `testaurant_bff/.env`
   - Frontend: `testaurant_ui/.env`

3. Ensure all services are running:
   - MongoDB: `mongosh` should connect
   - Backend: `curl http://localhost:8080/app/health`
   - Frontend: Browser should load `http://localhost:5173`

---

**Happy Testing! 🧪**

chmod 400 ~/Downloads/key.pem
ls -l ~/Downloads/key.pem
ssh -i ~/Downloads/key.pem ec2-user@51.20.37.236
