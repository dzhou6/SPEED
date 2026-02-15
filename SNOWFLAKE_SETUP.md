# Snowflake Integration Setup

This guide explains how to set up Snowflake for dual-database storage (MongoDB + Snowflake).

## Overview

The application now supports dual-write pattern:
- **MongoDB**: Primary operational database (fast, real-time)
- **Snowflake**: Analytics/warehouse database (historical data, analytics)

Data is written to both databases asynchronously. If Snowflake is unavailable, the app continues to work normally (MongoDB is the source of truth).

## Prerequisites

1. Snowflake account (free trial available at https://snowflake.com)
2. Snowflake warehouse, database, and schema created

## Setup Steps

### 1. Create Snowflake Tables

Run the SQL script in your Snowflake worksheet:

```bash
# The SQL script is located at:
backend/snowflake_setup.sql
```

Or manually run:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    role_prefs VARCHAR,
    skills VARCHAR,
    availability VARCHAR,
    course_codes VARCHAR,
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ
);

-- Swipes table
CREATE TABLE IF NOT EXISTS swipes (
    swipe_id VARCHAR PRIMARY KEY,
    from_user_id VARCHAR,
    to_user_id VARCHAR,
    course_code VARCHAR,
    decision VARCHAR,
    created_at TIMESTAMP_NTZ
);

-- Pods table
CREATE TABLE IF NOT EXISTS pods (
    pod_id VARCHAR PRIMARY KEY,
    course_code VARCHAR,
    member_ids VARCHAR,
    leader_id VARCHAR,
    created_at TIMESTAMP_NTZ
);
```

### 2. Configure Environment Variables

Add these to your `.env` file:

```env
# Snowflake Configuration (optional - app works without it)
SNOWFLAKE_ACCOUNT=your_account_identifier
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse_name
SNOWFLAKE_DATABASE=your_database_name
SNOWFLAKE_SCHEMA=PUBLIC  # or your schema name
```

**Note**: If Snowflake credentials are not provided, the app will work normally without Snowflake sync.

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `snowflake-connector-python`.

### 4. Test the Integration

1. Start the backend server
2. Create a user or make a swipe
3. Check Snowflake tables to verify data is being written

## How It Works

### Dual Write Pattern

When data is written to MongoDB:
1. Write succeeds to MongoDB (primary)
2. Async task writes to Snowflake (non-blocking)
3. If Snowflake fails, error is logged but request succeeds

### Endpoints with Dual Write

- `/auth/demo` - User creation
- `/profile` - User profile updates
- `/swipe` - Swipe events and pod formations

### Data Flow

```
User Request → FastAPI
                ↓
        ┌───────┴───────┐
        ↓               ↓
    MongoDB         Snowflake
    (Primary)       (Analytics)
```

## Troubleshooting

### Snowflake connection fails

- Check credentials in `.env`
- Verify warehouse is running
- Check network access (IP allowlist if needed)
- Check logs for specific error messages

### Data not appearing in Snowflake

- Verify tables exist
- Check application logs for Snowflake errors
- Ensure Snowflake credentials are correct
- Check that async tasks are running (check logs)

### App works but Snowflake sync doesn't

This is expected if:
- Snowflake credentials are missing (app works without them)
- Snowflake connection fails (non-blocking, doesn't affect app)

Check logs for warnings like: `Failed to write user to Snowflake: ...`

## Benefits

### MongoDB Track
- Fast, scalable NoSQL database
- Real-time operations
- Document-based data model

### Snowflake Track
- Data warehousing capabilities
- Analytics and BI integration
- Historical data storage
- Dual-database architecture showcase

## Next Steps

- Query Snowflake for analytics (match rates, popular courses, etc.)
- Set up BI tools (Tableau, Power BI) connected to Snowflake
- Create dashboards for course administrators
