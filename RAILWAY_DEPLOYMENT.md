# 🚂 Railway Deployment Guide

## Your Django RAG Chatbot is now ready for Railway!

### ✅ Configuration Complete
- ✅ `railway.json` - Railway configuration
- ✅ `Procfile` - Process definition
- ✅ `requirements.txt` - Updated with gunicorn
- ✅ `settings.py` - Railway database support added

---

## 🚀 Step-by-Step Deployment

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Ready for Railway deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy on Railway

#### Option A: Using Railway Dashboard (Recommended)

1. **Sign up/Login**
   - Go to [railway.app](https://railway.app)
   - Sign up with GitHub (recommended)

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will detect Django automatically

3. **Add PostgreSQL Database**
   - In your project, click "+ New"
   - Select "Database" → "Add PostgreSQL"
   - Railway will automatically create `DATABASE_URL` env variable

4. **Configure Environment Variables**
   - Go to your service → "Variables"
   - Add these environment variables:

```env
SECRET_KEY=your-very-secret-key-change-this
DEBUG=False
ALLOWED_HOSTS=*.railway.app

# External Services
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=rag-chat-index
HF_TOKEN=your_huggingface_token
MODEL=openai/gpt-oss-20b

# Railway automatically provides DATABASE_URL - don't override it!
```

5. **Deploy**
   - Railway will automatically deploy when you push to GitHub
   - Or click "Deploy" in the dashboard
   - Wait for build to complete

6. **Run Migrations**
   - In Railway dashboard → Service → Deployments
   - Click on latest deployment
   - Open "View Logs"
   - Migrations run automatically from Procfile

#### Option B: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project or create new
railway link

# Add PostgreSQL
railway add --database postgres

# Set environment variables
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
# ... set other vars ...

# Deploy
railway up
```

---

## 📋 Environment Variables Checklist

Copy-paste these into Railway Variables:

```env
# Django
SECRET_KEY=change-this-to-random-string
DEBUG=False

# Supabase (for user management)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Pinecone (for vector search)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=rag-chat-index

# Hugging Face (for AI model)
HF_TOKEN=your-huggingface-token
MODEL=openai/gpt-oss-20b

# Database - Railway provides DATABASE_URL automatically!
```

---

## 🎯 Post-Deployment

### 1. Create Superuser
```bash
# In Railway dashboard → Service → Deployments → Click latest → Terminal
python manage.py createsuperuser
```

### 2. Set Custom Domain (Optional)
- Go to Settings → Domains
- Add your custom domain
- Railway provides SSL automatically

### 3. Monitor Logs
- Railway dashboard → Service → Deployments → View Logs
- Monitor errors and performance

---

## 💰 Railway Pricing

**Free Tier:**
- $5 credit/month (enough for this app!)
- Auto-sleeps after 7 days of inactivity
- Unlimited deploys
- Automatic SSL

**Hobby Plan ($5/month):**
- Always-on service
- No sleep
- Better performance

---

## 🔧 Troubleshooting

### Issue: Build fails
**Solution:** Check logs in Railway dashboard. Usually:
- Missing dependencies in requirements.txt ✅ (already fixed)
- Wrong Python version (Railway auto-detects)

### Issue: Database connection error
**Solution:** 
- Railway automatically creates `DATABASE_URL`
- Don't override it in environment variables
- Check PostgreSQL service is running

### Issue: Static files not loading
**Solution:**
- Already configured with WhiteNoise ✅
- Check `STATIC_ROOT` in settings.py

### Issue: 502 Bad Gateway
**Solution:**
- Check if service is sleeping (free tier)
- Upgrade to Hobby plan or wake service
- Check logs for errors

### Issue: Migrations not running
**Solution:**
- They run automatically from Procfile ✅
- Or run manually: `railway run python manage.py migrate`

---

## ✨ Features Working on Railway

✅ Django app runs on Gunicorn
✅ PostgreSQL database (auto-configured)
✅ Static files served via WhiteNoise
✅ Environment-based configuration
✅ Automatic migrations on deploy
✅ Production-ready settings

---

## 🚀 Quick Commands

```bash
# View logs
railway logs

# Open shell
railway shell

# Run migrations manually
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Collect static files
railway run python manage.py collectstatic
```

---

## 🎉 You're All Set!

Your Django RAG Chatbot is now deployed on Railway! 

**Next Steps:**
1. Visit your Railway URL (e.g., `https://your-app.railway.app`)
2. Test registration and login
3. Create a chat and test RAG functionality
4. (Optional) Set up custom domain

Need help? Check Railway docs: https://docs.railway.app

