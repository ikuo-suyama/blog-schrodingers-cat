#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, urljoin

# ディレクトリパス
HTML_DIRS = [
    "local_html/ikuoikuo_2005/e",
    "local_html/ikuoikuo_2005/m"
]

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
            if path_part.startswith('/'):
                return f"/assets/{domain}{path_part}"
            else:
                return f"/assets/{domain}/{path_part}"
    
    # Handle relative paths that should point to assets
    if path.startswith(('/css/', '/js/', '/img/', '/tpl_master/')):
        return f"/assets/blog.goo.ne.jp{path}"
    
    # Handle image paths that might be missing domain information
    if path.startswith('/assets/') and not any(domain in path for domain in ['blogimg.goo.ne.jp', 'blog.goo.ne.jp', 'i.xgoo.jp', 'u.xgoo.jp']):
        # Extract the filename
        filename = os.path.basename(path)
        # If it looks like an image file
        if any(filename.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
            # Assume it's from blogimg.goo.ne.jp
            return f"/assets/blogimg.goo.ne.jp/user_image/path/{filename}"
    
    return path

def fix_html_paths(directories):
    """Fix paths in HTML files across multiple directories"""
    total_files = 0
    modified_files = 0
    
    for directory in directories:
        html_files = list(Path(directory).glob("**/*.html"))
        
        if not html_files:
            print(f"No HTML files found in {directory}")
            continue
        
        total_files += len(html_files)
        print(f"Processing {len(html_files)} HTML files in {directory}...")
        
        for html_file in html_files:
            print(f"Processing {html_file}...")
            
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Track if any changes were made to this file
            changes_made = False
            
            # Fix asset paths in img tags
            for img in soup.find_all('img', src=True):
                original_src = img['src']
                new_src = fix_asset_path(original_src)
                if new_src != original_src:
                    img['src'] = new_src
                    changes_made = True
                    print(f"  Fixed img src: {original_src} -> {new_src}")
            
            # Fix image links in a tags (often galleries or enlarged images)
            for a in soup.find_all('a', href=True):
                original_href = a['href']
                # Only fix image links
                if any(ext in original_href.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    new_href = fix_asset_path(original_href)
                    if new_href != original_href:
                        a['href'] = new_href
                        changes_made = True
                        print(f"  Fixed img href: {original_href} -> {new_href}")
                # Specifically check for blogimg.goo.ne.jp links
                elif 'blogimg.goo.ne.jp' in original_href:
                    new_href = fix_asset_path(original_href)
                    if new_href != original_href:
                        a['href'] = new_href
                        changes_made = True
                        print(f"  Fixed blogimg href: {original_href} -> {new_href}")
            
            # Save the modified file if changes were made
            if changes_made:
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                modified_files += 1
    
    print(f"Completed. Modified {modified_files} out of {total_files} HTML files.")

if __name__ == "__main__":
    fix_html_paths(HTML_DIRS) 