import requests
from bs4 import BeautifulSoup
import os
import time
from urllib.parse import urljoin, urlparse

BASE_URL = "https://blog.goo.ne.jp/ikuoikuo_2005/"
START_ARCHIVE_URL = urljoin(BASE_URL, "arcv")
OUTPUT_DIR = "raw_html"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

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

def save_html(content, filename):
    """Saves HTML content to a file."""
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved {filepath}")
    except IOError as e:
        print(f"Error saving {filepath}: {e}")

def get_post_filename(url):
    """Generates a filename from a post URL."""
    path_parts = urlparse(url).path.strip('/').split('/')
    # Expecting format like /ikuoikuo_2005/e/unique_post_id
    if len(path_parts) >= 3 and path_parts[1] == 'e':
        return f"{path_parts[2]}.html"
    # Fallback if URL structure is different
    return os.path.basename(urlparse(url).path) + ".html"

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    current_archive_url = START_ARCHIVE_URL
    processed_archive_urls = set()
    page_num = 1

    while current_archive_url and current_archive_url not in processed_archive_urls:
        print(f"--- Processing Archive Page {page_num}: {current_archive_url} ---")
        processed_archive_urls.add(current_archive_url)
        archive_html = download_page(current_archive_url)

        if not archive_html:
            print(f"Failed to download archive page: {current_archive_url}, stopping.")
            break

        soup = BeautifulSoup(archive_html, 'html.parser')

        # Find post links (adjust selector based on actual HTML structure)
        # Looking for links within the main article list section
        post_links = []
        article_list_section = soup.find('div', id='main') # Heuristic, might need adjustment
        if article_list_section:
            for link in article_list_section.find_all('a', href=True):
                href = link['href']
                # Check if it looks like a post link (contains '/e/')
                if '/e/' in href and href.startswith(BASE_URL):
                     # Avoid duplicates from same page
                    if href not in [p[1] for p in post_links]:
                         post_links.append((link.text.strip(), href))


        if not post_links:
             print("No post links found on this archive page. Trying broader search...")
             # Fallback: find any link containing /e/
             for link in soup.find_all('a', href=True):
                 href = link['href']
                 absolute_href = urljoin(current_archive_url, href)
                 if '/e/' in absolute_href and absolute_href.startswith(BASE_URL):
                      if absolute_href not in [p[1] for p in post_links]:
                         post_links.append((link.text.strip(), absolute_href))


        print(f"Found {len(post_links)} potential post links.")

        for title, post_url in post_links:
             absolute_post_url = urljoin(current_archive_url, post_url)
             filename = get_post_filename(absolute_post_url)
             filepath = os.path.join(OUTPUT_DIR, filename)

             if not os.path.exists(filepath):
                 post_html = download_page(absolute_post_url)
                 if post_html:
                     save_html(post_html, filename)
                     time.sleep(1) # Be polite, wait 1 second between requests
                 else:
                     print(f"Skipping failed download: {absolute_post_url}")
             else:
                 print(f"Already downloaded: {filename}, skipping.")


        # Find the "Next Page" link (adjust selector based on actual HTML)
        next_page_link = soup.find('a', string='次ページ') # Assuming text content identifies the link
        if next_page_link and next_page_link['href']:
            current_archive_url = urljoin(current_archive_url, next_page_link['href'])
            page_num += 1
        else:
            print("No 'Next Page' link found.")
            current_archive_url = None # Stop the loop

        print("--- Finished Processing Archive Page ---")
        if current_archive_url:
            time.sleep(1) # Wait before fetching next archive page


    print("Blog download process finished.")

if __name__ == "__main__":
    main() 