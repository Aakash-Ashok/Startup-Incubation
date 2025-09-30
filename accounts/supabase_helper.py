# accounts/supabase_helper.py

import os
from datetime import datetime
from supabase import create_client, Client
from django.conf import settings

def upload_to_supabase(file, folder="uploads"):
    try:
        supabase = get_supabase_client()
        filename = f"{folder}/{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.name}"
        
        # Upload file
        result = supabase.storage.from_(settings.SUPABASE_BUCKET).upload(filename, file.read())
        if isinstance(result, dict) and result.get('error'):
            print(f"Supabase Upload Failed: {result['error']}")
            return None

        # Get public URL
        public_url_dict = supabase.storage.from_(settings.SUPABASE_BUCKET).get_public_url(filename)
        public_url = public_url_dict.get('publicURL')  # <-- fixed key name

        if not public_url:
            print("Supabase Upload Warning: No public URL returned")
            return None

        return public_url

    except Exception as e:
        print("Supabase Upload Exception:", e)
        return None
