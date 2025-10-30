# How to Get DATABASE_URL in Railway

## What is DATABASE_URL?
It's a connection string that looks like:
```
postgresql://postgres:password@hostname:5432/database_name
```

## How to Find It in Railway:

### Method 1: From PostgreSQL Service (Easiest)
1. Click on your **"Postgres"** service in Railway
2. Go to the **"Variables"** tab
3. You'll see `DATABASE_URL` or `PGDATABASE_URL`
4. Copy the value (it's the connection string)

### Method 2: From PostgreSQL Service → Connect Tab
1. Click on **"Postgres"** service
2. Look for **"Connect"** or **"Connection"** tab
3. Railway shows connection details there
4. Copy the connection string

### Method 3: Add to Django Service Manually
If Railway doesn't auto-inject it:

1. Go to your **"web"** (Django) service
2. Click **"Variables"** tab
3. Click **"+ New Variable"**
4. Name: `DATABASE_URL`
5. Value: Get from Postgres service variables

## What to Look For:

In your Postgres service, you should see variables like:
- `DATABASE_URL` ✅ (this is what we need!)
- `PGDATABASE`
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`

## If You Don't See DATABASE_URL:

Railway might be using different variable names. Check:
- `PGDATABASE_URL`
- `POSTGRES_URL`
- Or combine: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`

## Quick Fix:

1. Click **Postgres** service → **Variables** tab
2. Look for any variable with "URL" in the name
3. Copy it
4. Go to **web** service → **Variables** tab
5. Add: `DATABASE_URL` = (paste the value)

Then restart your web service!

