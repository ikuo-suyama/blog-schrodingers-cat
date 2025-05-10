#!/usr/bin/env python3
import os
import re
from pathlib import Path

# ディレクトリパス
HTML_DIR = "local_html/ikuoikuo_2005/e"

def fix_html_paths():
    """HTMLファイル内のパスを修正する"""
    html_files = list(Path(HTML_DIR).glob("**/*.html"))
    
    if not html_files:
        print(f"No HTML files found in {HTML_DIR}")
        return
    
    print(f"Processing {len(html_files)} HTML files...")
    
    # パス修正パターン
    path_patterns = [
        # /css/ から始まるパスを /assets/blog.goo.ne.jp/css/ に変換
        (r'(href=["\'])/css/([^"\']+)(["\'])', r'\1/assets/blog.goo.ne.jp/css/\2\3'),
        # /js/ から始まるパスを /assets/blog.goo.ne.jp/js/ に変換
        (r'(src=["\'])/js/([^"\']+)(["\'])', r'\1/assets/blog.goo.ne.jp/js/\2\3'),
        # /tpl_master/ から始まるパスを /assets/blog.goo.ne.jp/tpl_master/ に変換
        (r'(href=["\'])/tpl_master/([^"\']+)(["\'])', r'\1/assets/blog.goo.ne.jp/tpl_master/\2\3'),
        # その他のアセットパス
        (r'(href=["\']/[^"\']+\.(css|js|jpg|jpeg|png|gif|svg)(?:\?[^"\']*)?["\'])', r'\1'),
    ]
    
    modified_files = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # パターンに基づいてパスを修正
        for pattern, replacement in path_patterns:
            content = re.sub(pattern, replacement, content)
        
        # 変更があった場合のみファイルを上書き
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            modified_files += 1
            
            # 進捗表示
            if modified_files % 10 == 0:
                print(f"Modified {modified_files} files...")
    
    print(f"Completed. Modified {modified_files} HTML files.")

if __name__ == "__main__":
    fix_html_paths() 