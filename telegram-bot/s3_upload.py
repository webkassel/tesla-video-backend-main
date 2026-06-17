"""
Supabase Storage upload helper for video files
"""
import os
import logging
import httpx

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
BUCKET_NAME = 'videos'


def upload_to_s3(local_file_path: str, file_key: str) -> str:
    """
    Upload a file to Supabase Storage and return the public URL
    """
    if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY]):
        raise Exception("Supabase credentials not configured.")
    
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_key}"
    
    with open(local_file_path, 'rb') as f:
        file_data = f.read()
    
    headers = {
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'video/mp4',
    }
    
    with httpx.Client(timeout=600.0) as client:
        response = client.post(upload_url, content=file_data, headers=headers)
        
        if response.status_code not in [200, 201]:
            raise Exception(f"Upload failed: {response.status_code} {response.text}")
    
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_key}"
    logger.info(f"Upload successful: {public_url}")
    return public_url


def delete_from_s3(file_key: str) -> bool:
    """Delete a file from Supabase Storage"""
    if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY]):
        return False
    
    try:
        delete_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{file_key}"
        headers = {'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}'}
        
        with httpx.Client() as client:
            client.delete(delete_url, headers=headers)
        return True
    except Exception as e:
        logger.error(f"Delete failed: {e}")
        return False
