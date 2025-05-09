import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# Directories
LOCAL_HTML_DIR = "local_html"
BLOG_SUBDIR = os.path.join(LOCAL_HTML_DIR, "ikuoikuo_2005")

def find_all_html_files(directory):
    """Find all HTML files in the given directory recursively"""
    html_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def update_backnumber_links(html_content):
    """Update backnumber links to include .html extension"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the backnumber section
    backnumber_module = soup.find('div', id='mod-back-numbers-scroll')
    if not backnumber_module:
        # Try by heading text if ID not found
        for h4 in soup.find_all('h4'):
            if 'バックナンバー' in h4.text:
                backnumber_module = h4.find_parent('div', class_='module')
                break
    
    if not backnumber_module:
        return html_content, 0  # No changes made
    
    # Update links in the backnumber module
    link_count = 0
    for a_tag in backnumber_module.find_all('a', href=True):
        href = a_tag['href']
        # Check if it's a month archive link without .html extension
        if '/m/' in href and not href.endswith('.html'):
            # Add .html extension
            a_tag['href'] = href + '.html'
            link_count += 1
    
    return str(soup), link_count

def main():
    # Find all HTML files in the blog directory
    html_files = find_all_html_files(BLOG_SUBDIR)
    print(f"Found {len(html_files)} HTML files")
    
    # Update backnumber links in each file
    total_files_updated = 0
    total_links_updated = 0
    
    for filepath in html_files:
        try:
            # Read the HTML content
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Update backnumber links
            updated_content, links_updated = update_backnumber_links(html_content)
            
            # If changes were made, write the updated content back to the file
            if links_updated > 0:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                total_files_updated += 1
                total_links_updated += links_updated
                print(f"Updated {links_updated} links in {filepath}")
        except Exception as e:
            print(f"Error processing {filepath}: {str(e)}")
    
    print(f"\nTotal files updated: {total_files_updated}")
    print(f"Total links updated: {total_links_updated}")

if __name__ == "__main__":
    main() 