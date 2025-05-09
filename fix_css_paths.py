#!/usr/bin/env python3
import os
import re
from pathlib import Path

# ディレクトリパス
HTML_DIR = "local_html/ikuoikuo_2005"

def fix_html_paths():
    """ikuoikuo_2005ディレクトリ内のHTMLファイルのCSS参照を修正する"""
    html_files = list(Path(HTML_DIR).glob("*.html"))
    
    if not html_files:
        print(f"No HTML files found in {HTML_DIR}")
        return
    
    print(f"Processing {len(html_files)} HTML files...")
    
    # パス修正パターン
    path_patterns = [
        # /css/ から始まるパスを /assets/blog.goo.ne.jp/css/ に変換
        (r'href=["\']\/css\/([^"\']+)["\']', r'href="/assets/blog.goo.ne.jp/css/\1"'),
        # /js/ から始まるパスを /assets/blog.goo.ne.jp/js/ に変換
        (r'src=["\']\/js\/([^"\']+)["\']', r'src="/assets/blog.goo.ne.jp/js/\1"'),
        # /tpl_master/ から始まるパスを /assets/blog.goo.ne.jp/tpl_master/ に変換
        (r'href=["\']\/tpl_master\/([^"\']+)["\']', r'href="/assets/blog.goo.ne.jp/tpl_master/\1"'),
        # blog.goo.ne.jp のフルパスをアセットパスに変換
        (r'href=["\'](https?:\/\/blog\.goo\.ne\.jp\/[^"\']+)["\']', r'href="/assets/blog.goo.ne.jp/\1"'),
        # i.xgoo.jp のパスをアセットパスに変換
        (r'(href|src)=["\'](https?:)?\/\/i\.xgoo\.jp\/([^"\']+)["\']', r'\1="/assets/i.xgoo.jp/\3"'),
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
    
    print(f"Completed. Modified {modified_files} HTML files.")

if __name__ == "__main__":
    fix_html_paths() 