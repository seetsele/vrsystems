#!/usr/bin/env python3
"""
Supabase Auth Configuration Script
Updates redirect URLs and site URL for OAuth to work properly
"""

import requests
import json
import sys

# Configuration - UPDATE THESE VALUES
SUPABASE_PROJECT_REF = "zxgydzavblgetojqdtir"
SUPABASE_ACCESS_TOKEN = ""  # Get from: https://supabase.com/dashboard/account/tokens

# Redirect URLs to add
REDIRECT_URLS = [
    "http://localhost:3000",
    "http://localhost:3000/",
    "http://localhost:3000/dashboard.html",
    "http://localhost:3000/auth.html",
    "http://localhost:3000/auth-test.html",
    "http://localhost:3000/**"
]

SITE_URL = "http://localhost:3000"

def get_current_auth_config():
    """Fetch current auth configuration"""
    url = f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/config/auth"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching config: {response.status_code}")
        print(response.text)
        return None

def update_auth_config(site_url: str, redirect_urls: list):
    """Update auth configuration with new site URL and redirect URLs"""
    url = f"https://api.supabase.com/v1/projects/{SUPABASE_PROJECT_REF}/config/auth"
    headers = {
        "Authorization": f"Bearer {SUPABASE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # The uri_allow_list should be a comma-separated string
    uri_allow_list = ",".join(redirect_urls)
    
    payload = {
        "site_url": site_url,
        "uri_allow_list": uri_allow_list
    }
    
    print(f"\nUpdating auth configuration...")
    print(f"  Site URL: {site_url}")
    print(f"  Redirect URLs: {redirect_urls}")
    
    response = requests.patch(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        print("\n✅ Auth configuration updated successfully!")
        return response.json()
    else:
        print(f"\n❌ Error updating config: {response.status_code}")
        print(response.text)
        return None

def main():
    if not SUPABASE_ACCESS_TOKEN:
        print("=" * 60)
        print("SUPABASE AUTH CONFIGURATION SCRIPT")
        print("=" * 60)
        print("\n❌ No access token provided!")
        print("\nTo use this script, you need a Personal Access Token:")
        print("1. Go to: https://supabase.com/dashboard/account/tokens")
        print("2. Click 'Generate new token'")
        print("3. Name it something like 'Verity Setup'")
        print("4. Copy the token")
        print("5. Paste it in this script (SUPABASE_ACCESS_TOKEN variable)")
        print("   OR run: python update_supabase_auth.py <YOUR_TOKEN>")
        print("\n" + "=" * 60)
        return
    
    print("=" * 60)
    print("SUPABASE AUTH CONFIGURATION")
    print("=" * 60)
    print(f"\nProject: {SUPABASE_PROJECT_REF}")
    
    # Get current config
    print("\nFetching current configuration...")
    current_config = get_current_auth_config()
    
    if current_config:
        print(f"\nCurrent Site URL: {current_config.get('site_url', 'Not set')}")
        print(f"Current Redirect URLs: {current_config.get('uri_allow_list', 'Not set')}")
        print(f"Google OAuth Enabled: {current_config.get('external_google_enabled', False)}")
        print(f"GitHub OAuth Enabled: {current_config.get('external_github_enabled', False)}")
    
    # Update config
    result = update_auth_config(SITE_URL, REDIRECT_URLS)
    
    if result:
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Test OAuth login at: http://localhost:3000/auth-test.html")
        print("2. Try Google Sign In")
        print("3. Try GitHub Sign In")
        print("4. Try Email/Password signup")
        print("\n" + "=" * 60)

if __name__ == "__main__":
    # Allow token to be passed as command line argument
    if len(sys.argv) > 1:
        SUPABASE_ACCESS_TOKEN = sys.argv[1]
    
    main()
