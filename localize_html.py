#!/usr/bin/env python3
import os
import re
from pathlib import Path
import shutil

# ソースとなるHTMLディレクトリ
SOURCE_DIR = "raw_html"
# 修正後のHTMLを保存するディレクトリ
OUTPUT_DIR = "local_html"
# アセットが保存されているディレクトリ
ASSETS_DIR = "assets"

def convert_url_to_local_path(url):
    """URLをローカルアセットへのパスに変換する"""
    # 空のURLやJavaScriptなどのURLは無視
    if not url or url.startswith('javascript:') or url.startswith('#'):
        return url
    
    # 相対パスのURLはそのまま返す (既にローカル参照のため)
    if url.startswith('/') and not url.startswith('//'):
        # ルート相対パスの場合は適切に変換
        return f"../assets/blog.goo.ne.jp{url}"
    
    # プロトコルとドメイン部分を取り除く
    if url.startswith('//'):
        url = 'https:' + url
    
    if url.startswith(('http://', 'https://')):
        # URLパース処理
        parts = url.split('://', 1)[1].split('/', 1)
        domain = parts[0]
        path = parts[1] if len(parts) > 1 else ""
        
        # クエリパラメータがある場合は除去
        if '?' in path:
            path = path.split('?')[0]
        
        # アンカーがある場合は除去
        if '#' in path:
            path = path.split('#')[0]
        
        # ローカルパスを構築
        return f"../assets/{domain}/{path}"
    
    return url

def process_html_file(source_file, output_file):
    """HTMLファイル内のURLをローカルパスに変換する"""
    with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # href属性のURLを置換
    content = re.sub(r'href=(["\'])(.*?)\1', 
                    lambda m: f'href={m.group(1)}{convert_url_to_local_path(m.group(2))}{m.group(1)}',
                    content)
    
    # src属性のURLを置換
    content = re.sub(r'src=(["\'])(.*?)\1', 
                    lambda m: f'src={m.group(1)}{convert_url_to_local_path(m.group(2))}{m.group(1)}',
                    content)
    
    # 出力先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 修正したHTMLを保存
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_file

def process_all_html_files():
    """すべてのHTMLファイルを処理する"""
    # 出力先ディレクトリが存在する場合は削除
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    
    # 出力先ディレクトリを作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # すべてのHTMLファイルを処理
    html_files = list(Path(SOURCE_DIR).glob("**/*.html"))
    total_files = len(html_files)
    processed_files = 0
    
    print(f"Converting {total_files} HTML files...")
    
    for source_file in html_files:
        # 出力先ファイルパスを構築
        rel_path = source_file.relative_to(SOURCE_DIR)
        output_file = os.path.join(OUTPUT_DIR, str(rel_path))
        
        # HTMLファイル内のURLを変換
        processed_file = process_html_file(source_file, output_file)
        processed_files += 1
        
        if processed_files % 10 == 0 or processed_files == total_files:
            print(f"Processed {processed_files}/{total_files} files")
    
    print(f"Conversion completed. Files saved in '{OUTPUT_DIR}' directory")
    
    # HTMLファイルをブラウザで確認する方法を表示
    print("\nTo view the localized files in a browser:")
    print(f"1. Navigate to the {OUTPUT_DIR} directory")
    print(f"2. Open any HTML file in your browser")
    print("3. All assets should now be loaded from local paths")

def main():
    # アセットディレクトリが存在するか確認
    if not os.path.exists(ASSETS_DIR):
        print(f"Error: Assets directory '{ASSETS_DIR}' not found.")
        print("Please run download_assets.py first to download assets.")
        return
    
    # HTMLファイルの変換処理
    process_all_html_files()

if __name__ == "__main__":
    main() 