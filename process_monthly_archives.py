import os
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Directories
RAW_HTML_DIR = "raw_html/monthly_archives"
LOCAL_HTML_DIR = "local_html"
MONTHLY_ARCHIVE_DIR = os.path.join(LOCAL_HTML_DIR, "ikuoikuo_2005", "m")

def ensure_directory_exists(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def extract_month_code(filename):
    """Extract the month code (YYYYMM) from the filename"""
    # Expected format: month_YYYYMM.html or month_YYYYMM_pageN.html
    parts = filename.split('_')
    if len(parts) >= 2:
        # Handle both month_YYYYMM.html and month_YYYYMM_pageN.html
        month_code = parts[1].split('.')[0]
        if '_page' in month_code:
            month_code = month_code.split('_page')[0]
        return month_code
    return None

def process_monthly_archive_html(html_content, month_code):
    """Process the HTML content of a monthly archive page"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process paths in the HTML content
    # 1. Fix asset paths (CSS, JS, images)
    for tag in soup.find_all(['link', 'script', 'img']):
        if tag.name == 'link' and tag.get('rel') and 'stylesheet' in tag.get('rel') and tag.get('href'):
            tag['href'] = fix_asset_path(tag['href'])
        elif tag.name == 'script' and tag.get('src'):
            tag['src'] = fix_asset_path(tag['src'])
        elif tag.name == 'img' and tag.get('src'):
            tag['src'] = fix_asset_path(tag['src'])
    
    # 2. Fix article links
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        
        # Fix article links (/ikuoikuo_2005/e/xxx.html)
        if '/ikuoikuo_2005/e/' in href or href.startswith('/e/'):
            a_tag['href'] = fix_article_link(href)
        # Fix other internal links
        elif href.startswith('/ikuoikuo_2005/') or href.startswith('https://blog.goo.ne.jp/ikuoikuo_2005/'):
            a_tag['href'] = fix_internal_link(href)
    
    return str(soup)

def fix_asset_path(path):
    """Fix asset paths to point to our local assets directory"""
    if path.startswith(('http://', 'https://')):
        # Extract the path part from URL
        parsed = urlparse(path)
        filename = os.path.basename(parsed.path)
        
        # Handle query parameters by removing them
        if '?' in filename:
            filename = filename.split('?')[0]
            
        return f"/assets/{filename}"
    return path

def fix_article_link(href):
    """Fix article links to the format /ikuoikuo_2005/e/xxx.html"""
    # Extract the article ID
    parsed = urlparse(href)
    path_parts = parsed.path.strip('/').split('/')
    
    if 'e' in path_parts:
        e_index = path_parts.index('e')
        if e_index + 1 < len(path_parts):
            article_id = path_parts[e_index + 1]
            return f"/ikuoikuo_2005/e/{article_id}.html"
    
    # If we can't parse it properly, return the original
    return href

def fix_internal_link(href):
    """Fix other internal links"""
    parsed = urlparse(href)
    path = parsed.path
    
    # Make sure the path starts with /ikuoikuo_2005/
    if 'ikuoikuo_2005' in path:
        parts = path.split('ikuoikuo_2005')
        return f"/ikuoikuo_2005{parts[1]}"
    
    return href

def main():
    # Ensure the local HTML directory for monthly archives exists
    ensure_directory_exists(MONTHLY_ARCHIVE_DIR)
    
    # Get all monthly archive files
    monthly_files = [f for f in os.listdir(RAW_HTML_DIR) if f.endswith('.html')]
    
    for filename in monthly_files:
        filepath = os.path.join(RAW_HTML_DIR, filename)
        
        # Extract the month code (YYYYMM)
        month_code = extract_month_code(filename)
        if not month_code:
            print(f"Could not extract month code from {filename}, skipping.")
            continue
        
        # Read the HTML content
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Process the HTML content
        processed_html = process_monthly_archive_html(html_content, month_code)
        
        # Save the processed HTML to the local HTML directory
        output_path = os.path.join(MONTHLY_ARCHIVE_DIR, f"{month_code}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_html)
        
        print(f"Processed {filename} -> {output_path}")
    
    print(f"Processed {len(monthly_files)} monthly archive files.")

if __name__ == "__main__":
    main() 