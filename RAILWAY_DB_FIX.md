# Railway Database Connection Fix

## The Problem:
Railway is trying to connect to Supabase database instead of Railway's PostgreSQL.

## The Solution:
Railway automatically provides `DATABASE_URL` when you connect a PostgreSQL database.

## Steps to Fix:

1. **Check PostgreSQL is Connected:**
   - In Railway dashboard, make sure you have a PostgreSQL service
   - It should show "Connected" with a green status

2. **Verify DATABASE_URL exists:**
   - Go to your Django service → Variables
   - You should see `DATABASE_URL` automatically (don't add it manually)
   - If it's not there, the PostgreSQL service might not be connected

3. **Connect PostgreSQL to Django Service:**
   - In your Railway project
   - Click on your PostgreSQL service
   - Click "Connect" or ensure it's connected to your Django service
   - Railway will automatically inject `DATABASE_URL`

4. **Redeploy:**
   - After connecting PostgreSQL, Railway will auto-redeploy
   - Or manually trigger a new deployment

## If Still Not Working:

Make sure PostgreSQL service:
- ✅ Is in the same Railway project
- ✅ Shows as "Connected"
- ✅ DATABASE_URL appears in Django service variables (automatically)

## Alternative: Use Supabase (If Railway DB not working)

If you prefer to use Supabase instead:
1. Remove Railway PostgreSQL service
2. Add these environment variables:
   - `SUPABASE_DB_NAME`
   - `SUPABASE_DB_USER`
   - `SUPABASE_DB_PASSWORD`
   - `SUPABASE_DB_HOST`
   - `SUPABASE_DB_PORT`

But Railway PostgreSQL is recommended - it's faster and free!

