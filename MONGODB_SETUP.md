# MongoDB Atlas Setup Guide

## Quick Setup (5 minutes)

### Step 1: Create Account
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" or "Sign Up"
3. Create account (use Google/GitHub for faster signup)

### Step 2: Create Cluster
1. Choose **Free Tier (M0)** - Shared cluster
2. Select cloud provider (AWS recommended)
3. Choose region closest to you
4. Click "Create Cluster"
5. Wait 3-5 minutes for cluster to provision

### Step 3: Create Database User
1. Go to **Database Access** (left sidebar)
2. Click "Add New Database User"
3. Choose "Password" authentication
4. Username: `coursecupid` (or your choice)
5. Password: Generate secure password (save it!)
6. Database User Privileges: **Read and write to any database**
7. Click "Add User"

### Step 4: Configure Network Access (IP Whitelist)
1. Go to **Network Access** (left sidebar)
2. Click "Add IP Address"
3. For **development/testing:**
   - Click "Allow Access from Anywhere"
   - This adds `0.0.0.0/0` (allows all IPs)
   - ⚠️ Only use this for development!
4. For **production:**
   - Click "Add Current IP Address" (adds your IP)
   - Or manually add specific IPs
5. Click "Confirm"

### Step 5: Get Connection String
1. Go to **Database** (left sidebar)
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Driver: **Python**, Version: **3.6 or later**
5. Copy the connection string
   - Looks like: `mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority`
6. Replace `<username>` with your database username
7. Replace `<password>` with your database password
8. Add database name at the end: `...mongodb.net/coursecupid?retryWrites=true&w=majority`

### Step 6: Add to .env File
```env
MONGO_URI=mongodb+srv://coursecupid:yourpassword@cluster0.xxxxx.mongodb.net/coursecupid?retryWrites=true&w=majority
MONGO_DB=coursecupid
```

## Collections & Indexes

The backend will auto-create collections when needed. No manual setup required!

Collections used:
- `users` - User profiles
- `pods` - Student pods
- `swipes` - Swipe decisions
- `presence` - Activity tracking
- `courses` - Course data
- `tickets` - Help tickets

## Troubleshooting

**"IP not whitelisted" error:**
- Go to Network Access → Add your current IP
- Or use `0.0.0.0/0` for development (less secure)

**"Authentication failed" error:**
- Check username/password in connection string
- Verify database user exists in Database Access
- Make sure password doesn't have special characters that need URL encoding

**"Connection timeout" error:**
- Check internet connection
- Verify cluster is running (not paused)
- Check firewall settings

**"Database not found" error:**
- MongoDB creates databases automatically on first write
- Run seed script: `python -m app.seed_demo`
- This will create the `coursecupid` database

## Free Tier Limits

- **Storage:** 512 MB (plenty for demo)
- **RAM:** Shared
- **Network:** Limited bandwidth
- **Perfect for:** Development, demos, small projects

## Security Notes

- ⚠️ Never commit `.env` file to git
- ⚠️ Use `0.0.0.0/0` only for development
- ⚠️ Use strong database passwords
- ✅ For production, whitelist specific IPs only
