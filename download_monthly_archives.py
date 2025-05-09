import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse

BASE_URL = "https://blog.goo.ne.jp/ikuoikuo_2005/"
OUTPUT_DIR = "raw_html"
MONTH_ARCHIVE_DIR = os.path.join(OUTPUT_DIR, "monthly_archives")
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# List of monthly archive URLs extracted from the HTML
MONTH_ARCHIVES = [
    # Format: YYYYMM (Year and Month)
    "201004", "200911", "200906", "200903", "200902", 
    "200810", "200809", "200807", "200803", "200802", "200801",
    "200712", "200711", "200710", "200708", "200707", "200706", "200705", "200704", "200703", "200702", "200701",
    "200612", "200611", "200610", "200609", "200608", "200607", "200606", "200605", "200604", "200603", "200602", "200601",
    "200512", "200511", "200510"
]

def download_page(url):
    """Downloads the HTML content of a given URL."""
    print(f"Fetching {url}...")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        # Explicitly set encoding based on HTTP headers or meta tags if necessary
        response.encoding = response.apparent_encoding
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_html(content, filename, directory):
    """Saves HTML content to a file in the specified directory."""
    filepath = os.path.join(directory, filename)
    try:
        # Ensure the directory exists before writing
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved {filepath}")
    except IOError as e:
        print(f"Error saving {filepath}: {e}")

def main():
    # Create output directories if they don't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(MONTH_ARCHIVE_DIR, exist_ok=True)
    
    # Download each monthly archive
    for month_code in MONTH_ARCHIVES:
        # Construct the URL for the monthly archive
        month_url = urljoin(BASE_URL, f"m/{month_code}")
        
        # Create a filename based on the month code
        filename = f"month_{month_code}.html"
        filepath = os.path.join(MONTH_ARCHIVE_DIR, filename)
        
        # Skip if already downloaded
        if os.path.exists(filepath):
            print(f"Already downloaded: {filename}, skipping.")
            continue
            
        html_content = download_page(month_url)
        if html_content:
            save_html(html_content, filename, MONTH_ARCHIVE_DIR)
            
            # Check for pagination in monthly archives
            soup = BeautifulSoup(html_content, 'html.parser')
            pagination_links = soup.find_all('a', string=lambda s: s and ('次ページ' in s or 'Next Page' in s))
            
            page_num = 2
            for page_link in pagination_links:
                if 'href' in page_link.attrs:
                    next_page_url = urljoin(month_url, page_link['href'])
                    page_filename = f"month_{month_code}_page{page_num}.html"
                    page_filepath = os.path.join(MONTH_ARCHIVE_DIR, page_filename)
                    
                    if not os.path.exists(page_filepath):
                        page_html = download_page(next_page_url)
                        if page_html:
                            save_html(page_html, page_filename, MONTH_ARCHIVE_DIR)
                            page_num += 1
                            time.sleep(1)  # Be polite, wait 1 second between requests
            
            # Wait between downloads to be respectful to the server
            time.sleep(1)
        else:
            print(f"Failed to download {month_url}")
    
    print("Monthly archive download process finished.")

if __name__ == "__main__":
    main() 