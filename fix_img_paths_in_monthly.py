#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse, urljoin

# ディレクトリパス
HTML_DIRS = [
    "local_html/ikuoikuo_2005/m",  # 月別アーカイブ
]

def fix_image_paths(html_content):
    """Fix image paths in the HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all img tags
    img_tags = soup.find_all('img')
    modified = False
    
    for img in img_tags:
        if 'src' in img.attrs:
            src = img['src']
            
            # 特に blogimg.goo.ne.jp のパスで "path" が使われている場合を修正
            if '/assets/blogimg.goo.ne.jp/user_image/path/' in src:
                # リンク(a)タグを探す
                parent_a = img.find_parent('a')
                
                if parent_a and 'href' in parent_a.attrs:
                    href = parent_a['href']
                    
                    # href が正しい構造を持っている場合はそれを利用
                    if '/assets/blogimg.goo.ne.jp/user_image/' in href and not '/path/' in href:
                        # href から正しいパスを抽出
                        path_parts = href.split('/assets/blogimg.goo.ne.jp/user_image/')[1]
                        
                        # 新しいパスを構築
                        new_src = f"/assets/blogimg.goo.ne.jp/user_image/{path_parts}"
                        img['src'] = new_src
                        modified = True
                        print(f"Fixed: {src} -> {new_src}")
    
    if modified:
        return str(soup)
    else:
        return html_content

def process_html_files():
    """Process all HTML files in the given directories"""
    total_files = 0
    modified_files = 0
    
    for html_dir in HTML_DIRS:
        for root, _, files in os.walk(html_dir):
            for file in files:
                if file.endswith('.html'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                        
                        # Fix image paths
                        modified_content = fix_image_paths(html_content)
                        
                        # Write back if modified
                        if modified_content != html_content:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(modified_content)
                            modified_files += 1
                        
                        total_files += 1
                    except Exception as e:
                        print(f"Error processing {file_path}: {str(e)}")
    
    print(f"Processed {total_files} files, modified {modified_files} files.")

if __name__ == "__main__":
    process_html_files() 