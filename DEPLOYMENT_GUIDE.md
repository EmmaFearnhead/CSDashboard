# Conservation Solutions Translocation Dashboard - Deployment Guide

## 🚀 Quick Start for Independent Hosting

### 1. System Requirements
- **Node.js**: 16+ and npm/yarn
- **Python**: 3.9+ with pip
- **MongoDB**: Local instance or cloud (MongoDB Atlas)
- **Environment**: Linux/macOS/Windows with Docker (optional)

### 2. Project Structure
```
conservation-dashboard/
├── backend/
│   ├── server.py              # FastAPI backend
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Backend environment variables
├── frontend/
│   ├── src/                   # React source code
│   ├── package.json           # Node.js dependencies
│   └── .env                   # Frontend environment variables
├── deploy/
│   ├── docker-compose.yml     # Docker deployment
│   ├── nginx.conf             # Nginx configuration
│   └── deploy.sh              # Deployment script
└── README.md                  # This file
```

## 🔧 Quick Setup

### Option 1: Docker Deployment (Recommended)
```bash
# Clone/download your project
cd conservation-dashboard

# Start all services
docker-compose up -d

# Your app will be available at http://localhost:3000
```

### Option 2: Manual Setup
```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URL

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend setup (new terminal)
cd frontend
yarn install  # or npm install

# Configure environment
cp .env.example .env
# Edit .env with backend URL

# Start frontend
yarn start  # or npm start
```

## 🔒 Security Configuration

### 1. Environment Variables

**Backend (.env):**
```
MONGO_URL=mongodb://localhost:27017
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Frontend (.env):**
```
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_APP_NAME=Conservation Solutions Dashboard
```

### 2. Production Security Checklist

- [ ] **Change default passwords** and secret keys
- [ ] **Enable HTTPS** with SSL certificates
- [ ] **Configure CORS** properly for your domain
- [ ] **Set up MongoDB authentication**
- [ ] **Enable firewall** rules (only ports 80, 443, 22)
- [ ] **Regular backups** of database
- [ ] **Update dependencies** regularly

## 🌐 Cloud Deployment Options

### Option 1: DigitalOcean App Platform
1. Connect GitHub repository
2. Configure build and run commands
3. Add environment variables
4. Deploy automatically

### Option 2: AWS/GCP/Azure
1. Use container services (ECS, Cloud Run, Container Instances)
2. Set up managed database (Atlas, DocumentDB)
3. Configure CDN and load balancer
4. Set up monitoring

### Option 3: VPS (Linode, DigitalOcean Droplet)
1. Install Docker and Docker Compose
2. Clone repository
3. Configure environment variables
4. Run deployment script

## 📊 Database Management

### MongoDB Setup Options

**Local MongoDB:**
```bash
# Install MongoDB Community Edition
# Ubuntu/Debian:
sudo apt install mongodb-community

# macOS:
brew install mongodb-community

# Start service
sudo systemctl start mongod
```

**MongoDB Atlas (Cloud - Recommended):**
1. Sign up at https://cloud.mongodb.com
2. Create free cluster
3. Get connection string
4. Update MONGO_URL in backend/.env

### Backup & Restore
```bash
# Backup
mongodump --uri="mongodb://localhost:27017/conservation_dashboard" --out=backup/

# Restore
mongorestore --uri="mongodb://localhost:27017" backup/conservation_dashboard/
```

## 🔄 Data Management

### Excel Upload Management
- **Supported formats**: .xlsx, .xls, .csv
- **Column flexibility**: Automatically detects column names
- **Data validation**: Handles various coordinate and year formats
- **Backup**: Previous data is cleared before new uploads

### Data Security
- **Input validation**: All uploads are validated
- **Error handling**: Graceful failure with detailed logs
- **Data persistence**: Automatic UUID generation for records

## 🛠️ Customization

### Frontend Customization
- **Colors**: Edit `frontend/src/App.css` for theme colors
- **Logo**: Replace logo in `frontend/public/`
- **Content**: Modify text in `frontend/src/App.js`

### Backend Customization
- **API endpoints**: Add/modify in `backend/server.py`
- **Data models**: Update Pydantic models
- **Validation rules**: Modify species categorization logic

## 📈 Monitoring & Maintenance

### Health Monitoring
```bash
# Check backend health
curl http://localhost:8001/api/

# Check database connection
curl http://localhost:8001/api/translocations/stats
```

### Log Management
- **Backend logs**: Check application logs for errors
- **Database logs**: Monitor MongoDB performance
- **Frontend logs**: Check browser console for issues

### Regular Maintenance
- [ ] **Weekly database backups**
- [ ] **Monthly dependency updates**
- [ ] **Quarterly security reviews**
- [ ] **Performance monitoring**

## 🆘 Troubleshooting

### Common Issues

**Upload not working:**
- Check file format is .xlsx, .xls, or .csv
- Verify column headers contain keywords like "project", "year", "species"
- Check backend logs for detailed error messages

**Map not displaying:**
- Verify API endpoint returns data: `curl http://localhost:8001/api/translocations`
- Check browser console for JavaScript errors
- Ensure coordinates are in decimal degree format

**Database connection issues:**
- Verify MongoDB is running: `sudo systemctl status mongod`
- Check connection string in backend/.env
- Test connection: `mongo mongodb://localhost:27017`

## 📞 Support

For technical issues:
1. Check logs first (backend and frontend)
2. Verify environment configuration
3. Test API endpoints individually
4. Check database connectivity

---

**Your Conservation Solutions Translocation Dashboard is ready for production deployment!**

Choose your preferred hosting option and follow the setup guide above. The application is fully functional with robust Excel upload, data visualization, and secure data management.