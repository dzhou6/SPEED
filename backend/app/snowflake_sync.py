"""Snowflake sync utilities for dual-write pattern."""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from .snowflake_db import get_snowflake_connection, is_snowflake_available

logger = logging.getLogger(__name__)

async def write_user_to_snowflake(user_data: Dict[str, Any]):
    """Write user data to Snowflake (non-blocking)."""
    if not is_snowflake_available():
        return
    
    try:
        # Run in thread pool to avoid blocking
        await asyncio.to_thread(_write_user_sync, user_data)
    except Exception as e:
        logger.warning(f"Failed to write user to Snowflake: {e}")

def _write_user_sync(user_data: Dict[str, Any]):
    """Synchronous user write to Snowflake."""
    conn = get_snowflake_connection()
    if not conn:
        logger.warning("Snowflake connection is None in _write_user_sync")
        return
    
    try:
        cursor = conn.cursor()
        
        # Extract and convert data
        user_id = str(user_data.get("_id", ""))
        display_name = user_data.get("displayName", "") or ""
        role_prefs = str(user_data.get("rolePrefs", [])) if user_data.get("rolePrefs") else "[]"
        skills = str(user_data.get("skills", [])) if user_data.get("skills") else "[]"
        availability = str(user_data.get("availability", [])) if user_data.get("availability") else "[]"
        course_codes = str(user_data.get("courseCodes", [])) if user_data.get("courseCodes") else "[]"
        created_at = user_data.get("createdAt", datetime.now(timezone.utc))
        updated_at = datetime.now(timezone.utc)
        
        # Convert datetime to string if needed
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()
        
        # Check if user exists first
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing user
            cursor.execute("""
                UPDATE users SET
                    display_name = %s,
                    role_prefs = %s,
                    skills = %s,
                    availability = %s,
                    course_codes = %s,
                    updated_at = %s
                WHERE user_id = %s
            """, (display_name, role_prefs, skills, availability, course_codes, updated_at, user_id))
        else:
            # Insert new user
            cursor.execute("""
                INSERT INTO users (user_id, display_name, role_prefs, skills, 
                                 availability, course_codes, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, display_name, role_prefs, skills, availability, course_codes, created_at, updated_at))
        
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        logger.info(f"Synced user {user_id} to Snowflake (rows affected: {rows_affected})")
    except Exception as e:
        logger.error(f"Error writing user to Snowflake: {e}", exc_info=True)

async def write_swipe_to_snowflake(swipe_data: Dict[str, Any]):
    """Write swipe data to Snowflake (non-blocking)."""
    if not is_snowflake_available():
        return
    
    try:
        await asyncio.to_thread(_write_swipe_sync, swipe_data)
    except Exception as e:
        logger.warning(f"Failed to write swipe to Snowflake: {e}")

def _write_swipe_sync(swipe_data: Dict[str, Any]):
    """Synchronous swipe write to Snowflake."""
    conn = get_snowflake_connection()
    if not conn:
        logger.warning("Snowflake connection is None in _write_swipe_sync")
        return
    
    try:
        cursor = conn.cursor()
        
        # Extract data
        from_user_id = str(swipe_data.get("fromUserId", ""))
        to_user_id = str(swipe_data.get("toUserId", ""))
        course_code = swipe_data.get("courseCode", "")
        decision = swipe_data.get("decision", "")
        created_at = swipe_data.get("createdAt", datetime.now(timezone.utc))
        swipe_id = f"{from_user_id}_{to_user_id}_{course_code}"
        
        # Convert datetime to string if needed
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        
        # Check if swipe exists first
        cursor.execute("SELECT swipe_id FROM swipes WHERE swipe_id = %s", (swipe_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing swipe
            cursor.execute("""
                UPDATE swipes SET
                    decision = %s,
                    created_at = %s
                WHERE swipe_id = %s
            """, (decision, created_at, swipe_id))
        else:
            # Insert new swipe
            cursor.execute("""
                INSERT INTO swipes (swipe_id, from_user_id, to_user_id, course_code, decision, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (swipe_id, from_user_id, to_user_id, course_code, decision, created_at))
        
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        logger.info(f"Synced swipe {swipe_id} to Snowflake (rows affected: {rows_affected})")
    except Exception as e:
        logger.error(f"Error writing swipe to Snowflake: {e}", exc_info=True)

async def write_pod_to_snowflake(pod_data: Dict[str, Any]):
    """Write pod data to Snowflake (non-blocking)."""
    if not is_snowflake_available():
        return
    
    try:
        await asyncio.to_thread(_write_pod_sync, pod_data)
    except Exception as e:
        logger.warning(f"Failed to write pod to Snowflake: {e}")

def _write_pod_sync(pod_data: Dict[str, Any]):
    """Synchronous pod write to Snowflake."""
    conn = get_snowflake_connection()
    if not conn:
        logger.warning("Snowflake connection is None in _write_pod_sync")
        return
    
    try:
        cursor = conn.cursor()
        
        # Extract data
        pod_id = str(pod_data.get("_id", ""))
        course_code = pod_data.get("courseCode", "")
        member_ids = pod_data.get("memberIds", [])
        leader_id = str(pod_data.get("leaderId", ""))
        created_at = pod_data.get("createdAt", datetime.now(timezone.utc))
        
        # Convert to strings
        member_ids_str = str([str(m) for m in member_ids]) if member_ids else "[]"
        
        # Convert datetime to string if needed
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        
        # Check if pod exists first
        cursor.execute("SELECT pod_id FROM pods WHERE pod_id = %s", (pod_id,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing pod
            cursor.execute("""
                UPDATE pods SET
                    course_code = %s,
                    member_ids = %s,
                    leader_id = %s
                WHERE pod_id = %s
            """, (course_code, member_ids_str, leader_id, pod_id))
        else:
            # Insert new pod
            cursor.execute("""
                INSERT INTO pods (pod_id, course_code, member_ids, leader_id, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (pod_id, course_code, member_ids_str, leader_id, created_at))
        
        conn.commit()
        rows_affected = cursor.rowcount
        cursor.close()
        logger.info(f"Synced pod {pod_id} to Snowflake (rows affected: {rows_affected})")
    except Exception as e:
        logger.error(f"Error writing pod to Snowflake: {e}", exc_info=True)
