import os
import sys
import zipfile
import tempfile
import requests
import json
from pathlib import Path
import msal

# MS Entra ID (M365) Application Configuration
# These can be overridden by environment variables
CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "your-azure-app-client-id")
TENANT_ID = os.getenv("AZURE_TENANT_ID", "common")  # common or specific tenant ID
GATEWAY_URL = os.getenv("CREWAI_GATEWAY_URL", "http://localhost:8000")

# Cache token locally to avoid frequent interactive logins
CACHE_DIR = Path.home() / ".crewai"
CACHE_PATH = CACHE_DIR / "token_cache.bin"

def load_token_cache():
    cache = msal.SerializableTokenCache()
    if CACHE_PATH.exists():
        try:
            with open(CACHE_PATH, "r") as f:
                cache.deserialize(f.read())
        except Exception as e:
            print(f"[Warning] Failed to load token cache: {e}")
    return cache

def save_token_cache(cache):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CACHE_PATH, "w") as f:
            f.write(cache.serialize())
    except Exception as e:
        print(f"[Warning] Failed to save token cache: {e}")

def get_auth_token():
    cache = load_token_cache()
    # Scopes: 'openid', 'profile', 'email' are standard OIDC scopes to get ID Token
    scopes = ["openid", "profile", "email"]
    
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=authority,
        token_cache=cache
    )
    
    # Try to get token from cache (silent login)
    accounts = app.get_accounts()
    if accounts:
        # Acquire token silently
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "id_token" in result:
            save_token_cache(cache)
            return result["id_token"]
            
    # If silent login fails, initiate Device Code Flow
    print("M365 (Microsoft Entra ID) Authentication Required.")
    flow = app.initiate_device_flow(scopes=scopes)
    if "user_code" not in flow:
        print("[Error] Failed to initiate Device Code Flow.")
        print(f"Details: {json.dumps(flow, indent=2)}")
        sys.exit(1)
        
    print(f"\n{flow['message']}\n")
    
    # Wait / poll for token
    result = app.acquire_token_by_device_flow(flow)
    if "id_token" in result:
        save_token_cache(cache)
        print("\nAuthentication Successful!\n")
        return result["id_token"]
    else:
        print(f"\n[Error] Authentication failed: {result.get('error_description', result.get('error'))}")
        sys.exit(1)

def zip_directory(dir_path, zip_file_path):
    print(f"Packaging crew source files from: {dir_path}")
    ignore_patterns = {
        ".git", ".venv", "venv", "__pycache__", "output", ".pytest_cache", 
        "node_modules", "zip", ".zip", "token_cache.bin", ".env"
    }
    
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dir_path):
            # Modify dirs in-place to prevent walking ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_patterns]
            
            for file in files:
                if any(file.endswith(ext) for ext in [".zip", ".pyc", ".pyo"]):
                    continue
                file_path = os.path.join(root, file)
                archive_name = os.path.relpath(file_path, dir_path)
                zipf.write(file_path, archive_name)

def deploy():
    # 1. Validate it is a valid Crew directory
    current_dir = os.getcwd()
    crew_name = os.path.basename(current_dir)
    print(f"Target Crew Name: {crew_name}")
    
    if not (os.path.exists("pyproject.toml") or os.path.exists("src")):
        print("[Error] deploy.py must be run from the root directory of a generated Crew project.")
        sys.exit(1)
        
    # 2. Authenticate
    try:
        id_token = get_auth_token()
    except Exception as e:
        print(f"[Error] Authentication process failed: {e}")
        sys.exit(1)
        
    # 3. Create temporary ZIP file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        temp_zip_path = temp_zip.name
        
    try:
        zip_directory(current_dir, temp_zip_path)
        
        # 4. Upload to gateway
        upload_url = f"{GATEWAY_URL}/api/v1/crews/deploy?overwrite=true"
        print(f"Uploading deployment package to {upload_url}...")
        
        headers = {
            "Authorization": f"Bearer {id_token}"
        }
        
        with open(temp_zip_path, "rb") as f:
            files = {
                "file": (f"{crew_name}.zip", f, "application/zip")
            }
            res = requests.post(upload_url, headers=headers, files=files, timeout=60)
            
        if res.status_code in (200, 201):
            print("\n==================================================")
            print("🎉 Deployment Completed Successfully!")
            res_data = res.json()
            print(res_data.get("message", "No message returned."))
            # Print audit logs
            meta = res_data.get("metadata", {})
            if meta:
                user = meta.get("deployed_by", {})
                print(f"Deployed by: {user.get('name')} ({user.get('email')}) [EmpID: {user.get('employee_id')}]")
                print(f"Deployed at: {meta.get('deployed_at')}")
            print("==================================================")
        else:
            print("\n==================================================")
            print(f"❌ Deployment Failed! (Status: {res.status_code})")
            try:
                err_detail = res.json().get("detail", res.text)
                print(f"Detail: {err_detail}")
            except Exception:
                print(f"Detail: {res.text}")
            print("==================================================")
            sys.exit(1)
            
    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)

if __name__ == "__main__":
    deploy()
