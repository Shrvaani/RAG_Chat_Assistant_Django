# How to Add PostgreSQL in Railway

## Step-by-Step Guide:

### 1. Go to Your Railway Project
- You should be on the project page showing "RAG_Chat_Assistant_Django" service

### 2. Look for "+ New" Button
- **Top right corner** of the project dashboard
- OR look for a button/icon that says "New" or "+"
- It might be in the sidebar or main area

### 3. Click "New" → Select "Database"
- Click the "+ New" button
- You'll see options like:
  - "Empty Service"
  - "Database"
  - "GitHub Repo"
  - etc.
- Click on **"Database"**

### 4. Select "PostgreSQL"
- After clicking "Database", you'll see:
  - PostgreSQL
  - MySQL
  - MongoDB
  - Redis
- Click **"PostgreSQL"**

### 5. Railway Creates It Automatically
- Railway will:
  - Create the PostgreSQL database
  - Automatically connect it to your Django service
  - Add `DATABASE_URL` environment variable (you'll see it in Variables tab)

### 6. Verify Connection
- Go to your Django service (RAG_Chat_Assistant_Django)
- Click **"Variables"** tab
- You should see `DATABASE_URL` listed (automatically added)

---

## If You Can't Find "+ New" Button:

### Alternative Method:
1. Click on your project name at the top
2. Look for "Services" section
3. There might be an "Add Service" or "+" button there

### Or Check Sidebar:
- Railway has a left sidebar
- Look for buttons/links to add services

---

## What You Should See After Adding:

1. ✅ Two services in your project:
   - RAG_Chat_Assistant_Django (your app)
   - PostgreSQL (new database)

2. ✅ In Django service → Variables:
   - `DATABASE_URL` automatically added (don't delete this!)

3. ✅ PostgreSQL service shows:
   - Connection details
   - Status: "Connected" or "Running"

---

## Still Can't Find It?

Try these:
- Refresh the page
- Look for "Add Service" instead of "New"
- Check if you're in the right project
- Try clicking around your project dashboard to find add/service buttons

Once PostgreSQL is added, Railway will automatically redeploy your Django app!

