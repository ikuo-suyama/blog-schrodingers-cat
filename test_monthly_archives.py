import requests
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8080/ikuoikuo_2005/m/"
LOCAL_ARCHIVES_DIR = "local_html/ikuoikuo_2005/m"

def get_all_monthly_archives():
    """Get all monthly archive files from the local_html directory"""
    archive_files = []
    for file in os.listdir(LOCAL_ARCHIVES_DIR):
        if file.endswith('.html'):
            archive_files.append(file)
    return archive_files

def test_url(url):
    """Test if a URL is accessible"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ {url} - OK ({len(response.content)} bytes)")
            return True
        else:
            print(f"❌ {url} - Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {url} - Exception: {str(e)}")
        return False

def main():
    # Wait a short time for the server to start
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Get all monthly archive files
    archive_files = get_all_monthly_archives()
    print(f"Found {len(archive_files)} monthly archive files to test")
    
    # Test each URL
    success_count = 0
    for file in archive_files:
        url = BASE_URL + file
        if test_url(url):
            success_count += 1
    
    print(f"\nResults: {success_count}/{len(archive_files)} URLs are accessible")

if __name__ == "__main__":
    main() 