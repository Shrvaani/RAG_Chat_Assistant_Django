# 🚂 Railway Deployment Steps

## ✅ Code Successfully Pushed to GitHub!
Repository: https://github.com/Shrvaani/RAG_Chat_Assistant_Django

---

## 🚀 Now Deploy to Railway:

### Step 1: Sign Up / Login to Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account (recommended)

### Step 2: Create New Project
1. Click **"New Project"** button
2. Select **"Deploy from GitHub repo"**
3. Authorize Railway to access your GitHub
4. Select repository: **RAG_Chat_Assistant_Django**
5. Click **"Deploy Now"**

### Step 3: Add PostgreSQL Database
1. In your Railway project, click **"+ New"** button
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically add `DATABASE_URL` environment variable

### Step 4: Configure Environment Variables
1. Go to your service (Django app)
2. Click **"Variables"** tab
3. Add these environment variables:

```env
SECRET_KEY=your-very-secret-key-here-change-this
DEBUG=False
ALLOWED_HOSTS=*.railway.app

# Supabase (User Management)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Pinecone (Vector Search)
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=rag-chat-index

# Hugging Face (AI Model)
HF_TOKEN=your-huggingface-token
MODEL=openai/gpt-oss-20b
```

**Important Notes:**
- Railway automatically provides `DATABASE_URL` - don't override it!
- Replace all values above with your actual API keys
- Get your keys from: Supabase Dashboard, Pinecone Dashboard, Hugging Face Settings

### Step 5: Wait for Deployment
1. Railway will automatically:
   - Install dependencies from `requirements.txt`
   - Run migrations (from Procfile)
   - Start the Django server with Gunicorn
2. Check **"Deployments"** tab for build logs
3. Wait for "Deploy Successful" status

### Step 6: Get Your App URL
1. Once deployed, go to **"Settings"** tab
2. Find **"Domains"** section
3. Click **"Generate Domain"** (or use the default)
4. Your app will be live at: `https://your-app.railway.app`

### Step 7: Create Superuser (Optional)
1. Go to **"Deployments"** → Latest deployment
2. Click **"View Logs"**
3. Open terminal or run:
```bash
railway run python manage.py createsuperuser
```

### Step 8: Test Your App
1. Visit your Railway URL
2. Register a new account
3. Create a chat
4. Test RAG functionality with PDF upload

---

## 🔧 Troubleshooting

### Build Fails?
- Check logs in Railway dashboard
- Ensure all dependencies are in `requirements.txt` ✅ (already done)

### Database Error?
- Verify PostgreSQL service is running
- Check `DATABASE_URL` is automatically set (don't override)
- Run migrations manually if needed

### Static Files Not Loading?
- Already configured with WhiteNoise ✅
- Check `STATIC_ROOT` in settings.py

### 502 Bad Gateway?
- Service might be sleeping (free tier)
- Wake it up or upgrade to Hobby plan
- Check logs for errors

---

## 💰 Railway Pricing

**Free Tier:** $5 credit/month (perfect for your app!)
- Auto-sleeps after 7 days inactivity
- Unlimited deploys
- Free PostgreSQL

**Hobby Plan:** $5/month
- Always-on service
- No sleep mode
- Better performance

---

## 📚 Next Steps

1. ✅ Code pushed to GitHub
2. ⏳ Deploy on Railway (follow steps above)
3. ⏳ Add environment variables
4. ⏳ Test your deployed app
5. ⏳ (Optional) Add custom domain

---

## 🎉 You're All Set!

Your Django RAG Chatbot is now on GitHub and ready for Railway deployment!

**Repository:** https://github.com/Shrvaani/RAG_Chat_Assistant_Django

Need help? Check Railway docs: https://docs.railway.app

