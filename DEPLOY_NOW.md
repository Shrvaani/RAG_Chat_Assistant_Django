# 🚀 DEPLOY TO RAILWAY - Step by Step

## Your Repository is Ready!
✅ GitHub: https://github.com/Shrvaani/RAG_Chat_Assistant_Django
✅ All files committed
✅ Railway config ready

---

## 🎯 EXACT STEPS TO DEPLOY:

### Step 1: Go to Railway
Visit: **https://railway.app/new**

### Step 2: Connect GitHub
1. You'll see "Deploy from GitHub repo" - click it
2. If asked to authorize, click **"Authorize Railway"** or **"Connect GitHub"**
3. Grant Railway access to your repositories

### Step 3: Find Your Repository
Once GitHub is connected, you'll see YOUR repositories. Look for:
- **RAG_Chat_Assistant_Django**
- Click on it to select

**If you still see "No repositories found":**
- Try clicking "Connect GitHub" button first
- Make sure you're logged into Railway with the SAME GitHub account
- Refresh the page after connecting

### Step 4: Deploy
1. Railway will detect it's a Django app automatically
2. Click **"Deploy"** or **"Deploy Now"**
3. Wait for initial deployment (will fail until you add env vars - that's OK!)

### Step 5: Add PostgreSQL Database
1. In your Railway project, click **"+ New"** button
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway automatically creates `DATABASE_URL` (don't add it manually!)

### Step 6: Add Environment Variables
Go to your Django service → **Variables** tab → Add these:

```
SECRET_KEY=change-this-to-a-random-secret-key-min-50-characters
DEBUG=False
ALLOWED_HOSTS=*.railway.app

PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=rag-chat-index
HF_TOKEN=your-huggingface-token
MODEL=openai/gpt-oss-20b
```

**Replace the values with YOUR actual API keys!**

### Step 7: Redeploy
After adding variables, Railway will auto-redeploy. Wait for:
✅ Build successful
✅ Deployment successful

### Step 8: Get Your URL
1. Go to **Settings** → **Domains**
2. Click **"Generate Domain"**
3. Your app is live! 🎉

---

## ⚠️ TROUBLESHOOTING:

### "No repositories found"
- Make sure you clicked "Connect GitHub" first
- Check you're using the same GitHub account
- Try searching just: `RAG_Chat_Assistant_Django`

### Still can't find it?
1. Go to https://railway.app/new/connect
2. Connect GitHub there first
3. Then go back to deploy

---

## 🎯 Quick Link to Start:
**https://railway.app/new** ← Click here to start!

---

## 📝 What You Need:
- Your Pinecone API Key  
- Your Hugging Face Token
- A random SECRET_KEY (generate at: https://djecrety.ir/ or use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)

Once deployed, share your Railway URL and I can help test it! 🚀

