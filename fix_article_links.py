#!/usr/bin/env python3
import os
import re
from pathlib import Path

# ディレクトリパス
HTML_DIR = "local_html/ikuoikuo_2005/e"

def fix_article_links():
    """ブログ記事へのリンクを修正する"""
    html_files = list(Path(HTML_DIR).glob("**/*.html")) + list(Path("local_html/ikuoikuo_2005").glob("*.html"))
    
    if not html_files:
        print(f"No HTML files found in {HTML_DIR}")
        return
    
    print(f"Processing {len(html_files)} HTML files...")
    
    # パス修正パターン
    path_patterns = [
        # https://blog.goo.ne.jp/ikuoikuo_2005/e/xxx 形式を /ikuoikuo_2005/e/xxx.html に変換
        (r'href=["\'](https?://blog\.goo\.ne\.jp/ikuoikuo_2005/e/([a-f0-9]+))["\']', r'href="/ikuoikuo_2005/e/\2.html"'),
        
        # /assets/blog.goo.ne.jp/ikuoikuo_2005/e/xxx 形式を /ikuoikuo_2005/e/xxx.html に変換
        (r'href=["\']/?assets/blog\.goo\.ne\.jp/ikuoikuo_2005/e/([a-f0-9]+)["\']', r'href="/ikuoikuo_2005/e/\1.html"'),
        
        # 相対パス ../ikuoikuo_2005/e/xxx 形式を /ikuoikuo_2005/e/xxx.html に変換
        (r'href=["\']\.\./ikuoikuo_2005/e/([a-f0-9]+)["\']', r'href="/ikuoikuo_2005/e/\1.html"'),
        
        # /ikuoikuo_2005/e/xxx 形式（.htmlなし）を /ikuoikuo_2005/e/xxx.html に変換
        (r'href=["\']/?ikuoikuo_2005/e/([a-f0-9]+)["\']((?!\.html).*?)', r'href="/ikuoikuo_2005/e/\1.html"\2'),
    ]
    
    modified_files = 0
    modified_links = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # パターンに基づいてパスを修正
        for pattern, replacement in path_patterns:
            # 各置換操作で何個のリンクが変更されたかカウント
            new_content, count = re.subn(pattern, replacement, content)
            modified_links += count
            content = new_content
        
        # 変更があった場合のみファイルを上書き
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            modified_files += 1
            
            # 進捗表示
            if modified_files % 10 == 0:
                print(f"Modified {modified_files} files...")
    
    print(f"Completed. Modified {modified_files} HTML files with {modified_links} links updated.")

if __name__ == "__main__":
    fix_article_links() 