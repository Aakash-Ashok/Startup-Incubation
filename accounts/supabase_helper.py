# accounts/supabase_helper.py

import os
from datetime import datetime
from supabase import create_client, Client
from django.conf import settings

def get_supabase_client() -> Client:
    """
    Initialize Supabase client using backend Service Role Key.
    Returns:
        Client: Supabase client instance
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def upload_to_supabase(file, folder="uploads"):
    """
    Upload a file to Supabase Storage and return its public URL.

    Args:
        file: Django InMemoryUploadedFile or File object
        folder: folder path inside the bucket (e.g., "startups" or "project_requirements")

    Returns:
        str: public URL of uploaded file or None if failed
    """
    try:
        supabase = get_supabase_client()

        # Build unique filename
        filename = f"{folder}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"

        # Upload file
        result = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(filename, file.read())

        # Check for errors
        if isinstance(result, dict) and result.get('error'):
            print(f"Supabase Upload Failed: {result['error']}")
            return None

        # Get public URL
        public_url_dict = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(filename)
        public_url = public_url_dict.get('publicUrl')
        if not public_url:
            print("Supabase Upload Warning: No public URL returned")
            return None

        return public_url

    except Exception as e:
        print("Supabase Upload Exception:", e)
        return None
