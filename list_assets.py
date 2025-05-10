#!/usr/bin/env python3
import os
import re
from pathlib import Path
import urllib.parse

# アセットファイルリストを保存するディレクトリ
ASSETS_DIR = "assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def extract_urls_from_html_files():
    """HTMLファイルからCSSとJSと画像のURLを抽出する"""
    html_files = list(Path("raw_html").glob("**/*.html"))
    
    if not html_files:
        print("No HTML files found in raw_html directory!")
        return {}
    
    print(f"Scanning {len(html_files)} HTML files for assets...")
    
    # 種類ごとにURLを保存するディクショナリ
    asset_urls = {
        'css': set(),
        'js': set(),
        'img': set(),
        'all': set()
    }
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # href属性からCSSファイルのURLを抽出（クエリパラメータを含む）
            css_urls = re.findall(r'href=["\'](.*?\.css(?:\?[^"\']*)?)["\']', content)
            
            # link rel="stylesheet"からもCSSファイルを抽出
            stylesheet_urls = re.findall(r'<link[^>]*rel=["\'](stylesheet|Stylesheet)["\'][^>]*href=["\'](.*?)["\']', content)
            stylesheet_urls = [url[1] for url in stylesheet_urls if url[1].endswith('.css') or '.css?' in url[1]]
            
            # src属性からJSファイルのURLを抽出（クエリパラメータを含む）
            js_urls = re.findall(r'src=["\'](.*?\.js(?:\?[^"\']*)?)["\']', content)
            
            # src属性から画像ファイルのURLを抽出
            img_patterns = [
                r'src=["\'](.*?\.(jpg|jpeg|png|gif|svg)(?:\?[^"\']*)?)["\']',
                r'background-image:\s*url\(["\']?(.*?\.(jpg|jpeg|png|gif|svg)(?:\?[^"\'\)]*)?)["\']?\)',
                r'content=["\'](.*?\.(jpg|jpeg|png|gif|svg)(?:\?[^"\']*)?)["\']'
            ]
            
            img_urls = []
            for pattern in img_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    if isinstance(matches[0], tuple):
                        img_urls.extend([match[0] for match in matches])
                    else:
                        img_urls.extend(matches)
            
            # CSSファイルを追加
            for url in css_urls + stylesheet_urls:
                # 重複するURLをフィルタリング
                if url and not url.startswith('#') and not url.startswith('javascript:'):
                    asset_urls['css'].add(url)
                    asset_urls['all'].add(url)
            
            # JSファイルを追加
            for url in js_urls:
                if url and not url.startswith('#') and not url.startswith('javascript:'):
                    asset_urls['js'].add(url)
                    asset_urls['all'].add(url)
            
            # 画像ファイルを追加
            for url in img_urls:
                if url and not url.startswith('#') and not url.startswith('javascript:'):
                    asset_urls['img'].add(url)
                    asset_urls['all'].add(url)
    
    return asset_urls

def normalize_urls(urls):
    """URLを正規化する"""
    normalized_urls = []
    for url in urls:
        # クエリパラメータとフラグメントを分離
        parsed_url = urllib.parse.urlparse(url)
        # 相対パスを処理
        if url.startswith('//'):
            normalized_url = f'https:{url}'
        elif url.startswith('/'):
            normalized_url = f'https://blog.goo.ne.jp{url}'
        elif not url.startswith(('http://', 'https://')):
            # 完全なURLではない場合、何らかのベースURLが必要
            normalized_url = url  # この場合はそのまま使用
        else:
            normalized_url = url
        
        normalized_urls.append(normalized_url)
    
    return normalized_urls

def save_asset_lists(asset_urls):
    """アセットのURLリストをカテゴリ別に保存する"""
    # パス別のファイル
    with open(os.path.join(ASSETS_DIR, "css_files.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(asset_urls['css']):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "js_files.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(asset_urls['js']):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "image_files.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(asset_urls['img']):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "all_assets.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(asset_urls['all']):
            f.write(f"{url}\n")
    
    # 正規化されたパス
    normalized_css = normalize_urls(asset_urls['css'])
    normalized_js = normalize_urls(asset_urls['js'])
    normalized_img = normalize_urls(asset_urls['img'])
    normalized_all = normalize_urls(asset_urls['all'])
    
    with open(os.path.join(ASSETS_DIR, "normalized_css_files.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(normalized_css):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "normalized_js_files.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(normalized_js):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "normalized_image_files.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(normalized_img):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "normalized_all_assets.txt"), 'w', encoding='utf-8') as f:
        for url in sorted(normalized_all):
            f.write(f"{url}\n")

def analyze_query_params(asset_urls):
    """クエリパラメータ付きのURLを分析する"""
    css_with_query = [url for url in asset_urls['css'] if '.css?' in url]
    js_with_query = [url for url in asset_urls['js'] if '.js?' in url]
    
    if css_with_query:
        print(f"\nFound {len(css_with_query)} CSS files with query parameters:")
        for url in css_with_query[:10]:  # 最初の10個だけ表示
            print(f"  - {url}")
        if len(css_with_query) > 10:
            print(f"  ... and {len(css_with_query) - 10} more")
    
    if js_with_query:
        print(f"\nFound {len(js_with_query)} JS files with query parameters:")
        for url in js_with_query[:10]:  # 最初の10個だけ表示
            print(f"  - {url}")
        if len(js_with_query) > 10:
            print(f"  ... and {len(js_with_query) - 10} more")

def main():
    # HTMLファイルからURLを抽出
    asset_urls = extract_urls_from_html_files()
    
    if not asset_urls:
        return
    
    # URLの種類ごとのカウント
    css_count = len(asset_urls['css'])
    js_count = len(asset_urls['js'])
    img_count = len(asset_urls['img'])
    total_count = len(asset_urls['all'])
    
    print(f"Found {total_count} unique asset URLs:")
    print(f"  CSS files: {css_count}")
    print(f"  JS files: {js_count}")
    print(f"  Image files: {img_count}")
    
    # クエリパラメータの分析
    analyze_query_params(asset_urls)
    
    # アセットのURLリストを保存
    save_asset_lists(asset_urls)
    
    print(f"\nAsset lists saved to {ASSETS_DIR}/ directory:")
    print("  css_files.txt - CSS ファイルのリスト")
    print("  js_files.txt - JS ファイルのリスト")
    print("  image_files.txt - 画像ファイルのリスト")
    print("  all_assets.txt - すべてのアセットファイル")
    print("  normalized_*.txt - 正規化されたURLリスト")

if __name__ == "__main__":
    main() 