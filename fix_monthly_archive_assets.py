#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, urljoin

# ディレクトリパス
MONTHLY_ARCHIVE_DIR = "local_html/ikuoikuo_2005/m"

def fix_asset_path(path):
    """Fix asset paths to point to our local assets directory"""
    if path.startswith(('http://', 'https://')):
        # Extract the path part from URL
        parsed = urlparse(path)
        domain = parsed.netloc
        path_part = parsed.path
        
        # Handle query parameters by removing them
        if '?' in path_part:
            path_part = path_part.split('?')[0]
        
        # For domain-specific paths, maintain domain structure
        if domain == "blogimg.goo.ne.jp":
            return f"/assets/blogimg.goo.ne.jp{path_part}"
        elif domain == "blog.goo.ne.jp":
            return f"/assets/blog.goo.ne.jp{path_part}"
        elif domain == "i.xgoo.jp":
            return f"/assets/i.xgoo.jp{path_part}"
        elif domain == "u.xgoo.jp":
            return f"/assets/u.xgoo.jp{path_part}"
        else:
            # For other domains, preserve the path structure
            # Instead of just using the filename, keep the whole path
            if path_part.startswith('/'):
                return f"/assets/{domain}{path_part}"
            else:
                return f"/assets/{domain}/{path_part}"
    
    # Handle relative paths that should point to assets
    if path.startswith(('/css/', '/js/', '/img/', '/tpl_master/')):
        return f"/assets/blog.goo.ne.jp{path}"
    
    return path

def fix_internal_link(href):
    """Fix internal blog links to keep the proper structure"""
    parsed = urlparse(href)
    path = parsed.path
    
    # Do not modify monthly archive links - preserve /m/ directory
    if '/m/' in path:
        parts = path.split('/m/')
        return f"/ikuoikuo_2005/m/{parts[1]}"
    
    # Keep article links format
    if '/e/' in path:
        parts = path.split('/e/')
        return f"/ikuoikuo_2005/e/{parts[1]}"
    
    return href

def fix_html_paths():
    """Fix paths in HTML files"""
    html_files = list(Path(MONTHLY_ARCHIVE_DIR).glob("**/*.html"))
    
    if not html_files:
        print(f"No HTML files found in {MONTHLY_ARCHIVE_DIR}")
        return
    
    print(f"Processing {len(html_files)} HTML files...")
    
    modified_files = 0
    
    for html_file in html_files:
        print(f"Processing {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Track if any changes were made to this file
        changes_made = False
        
        # Fix asset paths in link tags (CSS)
        for link in soup.find_all('link', href=True):
            original_href = link['href']
            new_href = fix_asset_path(original_href)
            if new_href != original_href:
                link['href'] = new_href
                changes_made = True
                print(f"  Fixed asset: {original_href} -> {new_href}")
        
        # Fix asset paths in script tags (JS)
        for script in soup.find_all('script', src=True):
            original_src = script['src']
            new_src = fix_asset_path(original_src)
            if new_src != original_src:
                script['src'] = new_src
                changes_made = True
                print(f"  Fixed asset: {original_src} -> {new_src}")
        
        # Fix asset paths in img tags
        for img in soup.find_all('img', src=True):
            original_src = img['src']
            new_src = fix_asset_path(original_src)
            if new_src != original_src:
                img['src'] = new_src
                changes_made = True
                print(f"  Fixed asset: {original_src} -> {new_src}")
        
        # Fix internal links in a tags
        for a in soup.find_all('a', href=True):
            original_href = a['href']
            # Only fix internal blog links
            if 'ikuoikuo_2005' in original_href or '/m/' in original_href or '/e/' in original_href:
                new_href = fix_internal_link(original_href)
                if new_href != original_href:
                    a['href'] = new_href
                    changes_made = True
                    print(f"  Fixed link: {original_href} -> {new_href}")
        
        # Save the modified file if changes were made
        if changes_made:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            modified_files += 1
    
    print(f"Completed. Modified {modified_files} HTML files.")

if __name__ == "__main__":
    fix_html_paths() 