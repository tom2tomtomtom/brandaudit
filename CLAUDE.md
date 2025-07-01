# AI Brand Audit Tool - Development & Production Guide

## Project Overview

The **AI Brand Audit Tool** is a comprehensive web application that provides sophisticated brand analysis and auditing capabilities powered by artificial intelligence. It analyzes brand consistency, market perception, competitive positioning, and provides actionable insights through external API integrations.

## 🚀 Quick Start

```bash
# Frontend Development
cd frontend
pnpm install
pnpm dev

# Backend Development  
cd backend
pip install -r requirements.txt
python src/main.py

# Production Testing
node test-production.js
```

## 📋 Current Production Status: 71% Ready

### ✅ Working Components
- **Frontend**: Fully deployed and functional at `https://brandaudit.up.railway.app`
- **UI/UX**: Complete React application with professional design
- **Navigation**: Multi-step workflow with progress indicators
- **Forms**: Brand search, file upload, analysis configuration
- **Performance**: Fast loading (63ms) with responsive design

### ❌ Critical Issues to Fix
- **Backend API**: Service not responding (502 errors)
- **CORS**: Backend not accessible from frontend
- **API Integration**: No real data flow between frontend/backend

## 🔧 Production Deployment

### Railway Configuration

**Frontend Service**: ✅ Working
- URL: `https://brandaudit.up.railway.app`
- Dockerfile: `frontend/Dockerfile`
- Build: Vite + React production build

**Backend Service**: ❌ Needs Fix
- URL: `https://backend-service-production-1b63.up.railway.app`
- Dockerfile: `backend/Dockerfile`
- Status: Deployed but not responding

### Required Environment Variables

The backend requires these API keys to be set in Railway:

```bash
# AI/LLM Service
OPENROUTER_API_KEY=sk-or-v1-...

# News Data
NEWS_API_KEY=...

# Brand Data
BRANDFETCH_API_KEY=...
OPENCORPORATES_API_KEY=...

# Application Config
FLASK_ENV=production
SECRET_KEY=brand-audit-production-secret-key-2025
JWT_SECRET_KEY=brand-audit-jwt-secret-key-2025
PORT=8000
```

## 🧪 Testing Requirements

### ⚠️ CRITICAL: Real Data Testing Only

**This project MUST be tested with real data and full functionality.**

- ❌ **NO mock data or dummy responses**
- ❌ **NO bypassing API calls**
- ❌ **NO accepting partial functionality**

### Testing Criteria for "PASSING"

A test is only considered **PASSING** if:

1. **Real Brand Search**: Can search for actual companies (e.g., "Apple", "Nike")
2. **Real File Upload**: Can upload actual brand assets and process them
3. **Real AI Analysis**: Uses actual LLM APIs to generate insights
4. **Real News Data**: Fetches actual news articles about the brand
5. **Real Scoring**: Provides genuine brand health scores based on data
6. **Complete Workflow**: Full 5-step process works end-to-end
7. **Real Results**: Displays actual analysis results, not placeholders

### Test Commands

```bash
# Comprehensive Production Test
node test-production.js

# Backend API Test
node test-backend.js

# Full Functionality Test
node test-full-functionality.js
```

**Expected Result**: 95%+ production readiness with all real data flowing.

## 🏗️ Application Architecture

### Frontend (React + Vite)
- **Framework**: React 18 with TypeScript support
- **UI**: Shadcn/ui components + Tailwind CSS
- **State**: Zustand for global state management
- **Routing**: React Router for navigation
- **API**: Axios-based service layer

### Backend (Flask + Python)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: SQLite (production) / PostgreSQL (scalable)
- **Authentication**: JWT with Flask-JWT-Extended
- **APIs**: OpenRouter, NewsAPI, Brandfetch, OpenCorporates
- **AI**: Claude 3 Haiku via OpenRouter for analysis

## 📊 Complete Feature Set

### 1. User Authentication
- Registration, login, JWT tokens
- Role-based access (user/admin)
- Profile management

### 2. Brand Discovery
- Company search by name/website
- Brand asset discovery via APIs
- Company information retrieval

### 3. Analysis Workflow
1. **Brand Search**: Enter company name/website
2. **Asset Upload**: Upload brand files (logos, screenshots)
3. **Analysis Config**: Choose analysis types
4. **Processing**: Real-time AI analysis
5. **Results**: Comprehensive brand audit report

### 4. Analysis Types
- **Visual Brand Analysis**: Logo consistency, color palette
- **Market Presence**: News coverage, sentiment analysis
- **Competitive Analysis**: Market positioning, benchmarking
- **Sentiment Analysis**: AI-powered brand perception

### 5. Reporting
- Brand health scoring (0-100)
- Executive summaries
- Detailed insights and recommendations
- Historical analysis comparison
- Export capabilities (PDF, JSON)

## 🔄 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Current user info
- `POST /api/auth/logout` - Logout

### Brand Analysis
- `POST /api/brand/search` - Search brand information
- `POST /api/upload` - Upload brand assets
- `POST /api/analyze` - Start brand analysis
- `GET /api/analyze/{id}/status` - Check analysis progress
- `GET /api/analyze/{id}/results` - Get analysis results
- `GET /api/analyses` - Get user's analysis history

### System
- `GET /api/health` - Application health check

## 🐛 Current Issues & Solutions

### Backend Service Not Starting

**Symptoms**: 502 errors, service not responding

**Debug Steps**:
1. Check Railway backend service logs
2. Verify environment variables are set
3. Test database connectivity
4. Validate Python dependencies

**Potential Fixes**:
```bash
# Check if backend starts locally
cd backend
python start.py

# Test API locally
curl http://localhost:8000/api/health
```

### CORS Issues

**Symptoms**: Frontend can't connect to backend

**Current Config**: `origins=["*"]` (should work)

**Debug**: Check if `Access-Control-Allow-Origin` headers are present

### Database Initialization

**Location**: `backend/src/main.py` line 205-210

**Ensures**: SQLite database and tables are created on startup

## 🚀 Getting to 100% Production Ready

### Immediate Fixes Needed

1. **Fix Backend Deployment**
   - Debug Railway backend service
   - Ensure Flask app starts properly
   - Verify port binding (8000)

2. **API Key Integration**
   - Confirm all API keys are set in Railway
   - Test each external API connection
   - Verify API quotas and limits

3. **End-to-End Testing**
   - Test complete workflow with real data
   - Verify file uploads work
   - Confirm AI analysis generates real results

### Production Optimization

1. **Performance**
   - Add Redis caching for API responses
   - Implement database connection pooling
   - Optimize bundle sizes

2. **Security**
   - Add rate limiting
   - Implement input validation
   - Add API key rotation

3. **Monitoring**
   - Add application logging
   - Implement health checks
   - Set up error tracking

## 🛠️ Development Workflow

### Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
export FLASK_ENV=development
python src/main.py

# Frontend
cd frontend
pnpm install
pnpm dev
```

### Production Deployment

```bash
# Commit changes
git add .
git commit -m "Production improvements"
git push

# Railway auto-deploys from main branch
# Monitor deployment in Railway dashboard
```

### Testing Protocol

1. **Never accept partial functionality**
2. **Always test with real API keys**
3. **Verify complete data flow**
4. **Test error handling with invalid inputs**
5. **Confirm all features work end-to-end**

## 📝 Troubleshooting Commands

```bash
# Test backend locally
cd backend && python -c "from src.main import app; print('✅ Backend imports OK')"

# Test frontend build
cd frontend && pnpm build

# Check API connectivity
curl -X GET https://backend-service-production-1b63.up.railway.app/api/health

# Run all tests
node test-production.js
```

## 🎯 Success Criteria

The project is considered **production-ready** when:

- ✅ Frontend loads without errors
- ✅ Backend API responds to all endpoints
- ✅ Real brand searches return actual data
- ✅ File uploads process successfully
- ✅ AI analysis generates real insights
- ✅ Complete workflow works end-to-end
- ✅ Historical analysis shows real data
- ✅ Reports contain actual brand metrics
- ✅ Performance is acceptable (< 3s load times)
- ✅ No JavaScript console errors

**Current Status**: 71% ready - Backend deployment is the main blocker.

---

## 📞 Support

For issues with:
- **Deployment**: Check Railway service logs
- **API Integration**: Verify environment variables
- **Testing**: Run `node test-production.js` for diagnostics
- **Performance**: Monitor network tab in browser dev tools

**Remember**: This tool must work with real data to be considered functional. No shortcuts or mock data in production testing.