-- Snowflake Table Setup Script for CourseCupid
-- Run this in your Snowflake worksheet to create the necessary tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    role_prefs VARCHAR,  -- JSON array as string
    skills VARCHAR,      -- JSON array as string
    availability VARCHAR, -- JSON array as string
    course_codes VARCHAR, -- JSON array as string
    created_at TIMESTAMP_NTZ,
    updated_at TIMESTAMP_NTZ
);

-- Swipes table (for analytics)
CREATE TABLE IF NOT EXISTS swipes (
    swipe_id VARCHAR PRIMARY KEY,
    from_user_id VARCHAR,
    to_user_id VARCHAR,
    course_code VARCHAR,
    decision VARCHAR,  -- 'accept' or 'pass'
    created_at TIMESTAMP_NTZ
);

-- Pods table
CREATE TABLE IF NOT EXISTS pods (
    pod_id VARCHAR PRIMARY KEY,
    course_code VARCHAR,
    member_ids VARCHAR,  -- JSON array as string
    leader_id VARCHAR,
    created_at TIMESTAMP_NTZ
);

-- Optional: Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_swipes_from_user ON swipes(from_user_id);
CREATE INDEX IF NOT EXISTS idx_swipes_to_user ON swipes(to_user_id);
CREATE INDEX IF NOT EXISTS idx_swipes_course ON swipes(course_code);
CREATE INDEX IF NOT EXISTS idx_pods_course ON pods(course_code);

-- Verify tables were created
SHOW TABLES;
