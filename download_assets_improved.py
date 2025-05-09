#!/usr/bin/env python3
import os
import re
import requests
import urllib.parse
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from tqdm import tqdm

# アセットを保存するベースディレクトリ
ASSETS_DIR = "assets"
# ダウンロード済みURLを記録するファイル
DOWNLOADED_FILE = os.path.join(ASSETS_DIR, "downloaded_urls.txt")

def extract_urls_from_html_files():
    """HTMLファイルからCSSとJSと画像のURLを抽出する"""
    html_files = list(Path("raw_html").glob("**/*.html"))
    urls = set()
    
    print(f"Scanning {len(html_files)} HTML files for assets...")
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # href属性からCSSファイルのURLを抽出（クエリパラメータを含む）
            css_urls = re.findall(r'href=["\'](.*?\.css(?:\?[^"\']*)?)["\']', content)
            # src属性からJSファイルのURLを抽出（クエリパラメータを含む）
            js_urls = re.findall(r'src=["\'](.*?\.js(?:\?[^"\']*)?)["\']', content)
            # src属性から画像ファイルのURLを抽出
            img_urls = re.findall(r'src=["\'](.*?\.(jpg|jpeg|png|gif|svg)(?:\?[^"\']*)?)["\']', content)
            img_urls = [url[0] for url in img_urls]  # タプルから最初の要素だけ取り出す
            
            # すべてのURLを結合
            all_urls = css_urls + js_urls + img_urls
            for url in all_urls:
                urls.add(url)
    
    # クエリパラメータ付きのURLの詳細な分析
    css_with_query = [url for url in urls if '.css?' in url]
    js_with_query = [url for url in urls if '.js?' in url]
    if css_with_query:
        print(f"\nFound {len(css_with_query)} CSS files with query parameters:")
        for url in css_with_query[:5]:  # 最初の5つだけ表示
            print(f"  - {url}")
        if len(css_with_query) > 5:
            print(f"  ... and {len(css_with_query) - 5} more")
    
    if js_with_query:
        print(f"\nFound {len(js_with_query)} JS files with query parameters:")
        for url in js_with_query[:5]:  # 最初の5つだけ表示
            print(f"  - {url}")
        if len(js_with_query) > 5:
            print(f"  ... and {len(js_with_query) - 5} more")
    
    return urls

def normalize_url(url):
    """URLを正規化する（プロトコルがない場合はhttpsを追加）"""
    if url.startswith('//'):
        return f'https:{url}'
    elif url.startswith('/'):
        # 相対パスの場合はベースURLを追加
        return f'https://blog.goo.ne.jp{url}'
    elif not url.startswith(('http://', 'https://')):
        return f'https://{url}'
    return url

def get_save_path(url):
    """URLからファイルを保存するパスを生成する"""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path.lstrip('/')
    
    # クエリパラメータがある場合、ファイル名にハッシュとして付加する
    if parsed_url.query:
        file_path, file_ext = os.path.splitext(path)
        path = f"{file_path}_{hash(parsed_url.query) % 10000:04d}{file_ext}"
    
    # ファイル名がないURLの場合はindex.htmlとする
    if path.endswith('/') or not path:
        path = path + 'index.html'
    
    # URLに拡張子がない場合
    if not os.path.splitext(path)[1]:
        path = path + '.html'
    
    return os.path.join(ASSETS_DIR, domain, path)

def load_downloaded_urls():
    """既にダウンロード済みのURLを読み込む"""
    downloaded_urls = set()
    if os.path.exists(DOWNLOADED_FILE):
        with open(DOWNLOADED_FILE, 'r') as f:
            for line in f:
                downloaded_urls.add(line.strip())
    return downloaded_urls

def save_downloaded_url(url):
    """ダウンロード済みのURLを保存する"""
    with open(DOWNLOADED_FILE, 'a') as f:
        f.write(f"{url}\n")

def download_file(url, downloaded_urls):
    """指定されたURLからファイルをダウンロードする"""
    normalized_url = normalize_url(url)
    
    # 既にダウンロード済みの場合はスキップ
    if normalized_url in downloaded_urls:
        return True
    
    save_path = get_save_path(normalized_url)
    
    # 保存先ディレクトリが存在しない場合は作成
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    try:
        # すでにファイルが存在する場合は完了としてマーク
        if os.path.exists(save_path):
            save_downloaded_url(normalized_url)
            return True
        
        # ダウンロード実行
        response = requests.get(normalized_url, timeout=10, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # リダイレクトされた場合は元のURLと実際のURLの両方を記録
            if response.url != normalized_url:
                save_downloaded_url(response.url)
            
            save_downloaded_url(normalized_url)
            return True
        else:
            print(f"Failed to download: {normalized_url}, status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error downloading {normalized_url}: {e}")
        return False

def download_with_progress(urls, downloaded_urls, max_workers=10):
    """進捗表示付きで並列ダウンロードする"""
    remaining_urls = [url for url in urls if normalize_url(url) not in downloaded_urls]
    
    if not remaining_urls:
        print("All files already downloaded")
        return
    
    print(f"Downloading {len(remaining_urls)} files...")
    
    with tqdm(total=len(remaining_urls), unit='file') as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for url in remaining_urls:
                future = executor.submit(download_file, url, downloaded_urls)
                future.add_done_callback(lambda p: pbar.update(1))
                futures.append(future)
            
            # すべてのダウンロードが完了するまで待機
            for future in futures:
                future.result()

def save_asset_lists(urls):
    """アセットのURLリストをカテゴリ別に保存する"""
    css_files = [url for url in urls if url.endswith('.css') or '.css?' in url]
    js_files = [url for url in urls if url.endswith('.js') or '.js?' in url]
    img_files = [url for url in urls if re.search(r'\.(jpg|jpeg|png|gif|svg)(?:\?[^\'\"]*)?$', url)]
    
    with open(os.path.join(ASSETS_DIR, "css_files.txt"), 'w') as f:
        for url in sorted(css_files):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "js_files.txt"), 'w') as f:
        for url in sorted(js_files):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "image_files.txt"), 'w') as f:
        for url in sorted(img_files):
            f.write(f"{url}\n")
    
    with open(os.path.join(ASSETS_DIR, "all_assets.txt"), 'w') as f:
        for url in sorted(urls):
            f.write(f"{url}\n")

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Download assets from HTML files')
    parser.add_argument('--threads', type=int, default=10, help='Number of download threads (default: 10)')
    parser.add_argument('--retry', action='store_true', help='Retry failed downloads')
    parser.add_argument('--scan-only', action='store_true', help='Only scan and list assets without downloading')
    args = parser.parse_args()
    
    # アセット用ディレクトリを作成
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # 既にダウンロード済みのURLを読み込む
    downloaded_urls = load_downloaded_urls()
    if args.retry:
        downloaded_urls = set()  # リトライモードの場合は全てダウンロード
    
    # HTMLファイルからURLを抽出
    urls = extract_urls_from_html_files()
    print(f"Found {len(urls)} unique URLs")
    
    # URLの種類ごとのカウント
    css_count = sum(1 for url in urls if url.endswith('.css') or '.css?' in url)
    js_count = sum(1 for url in urls if url.endswith('.js') or '.js?' in url)
    img_count = sum(1 for url in urls if re.search(r'\.(jpg|jpeg|png|gif|svg)(?:\?[^\'\"]*)?$', url))
    
    print(f"CSS files: {css_count}")
    print(f"JS files: {js_count}")
    print(f"Image files: {img_count}")
    
    # アセットのURLリストを保存
    save_asset_lists(urls)
    
    # scan-onlyモードの場合はここで終了
    if args.scan_only:
        print("Scan completed. Asset lists saved to the assets directory.")
        return
    
    # ダウンロード済みファイル数
    already_downloaded = sum(1 for url in urls if normalize_url(url) in downloaded_urls)
    print(f"Already downloaded: {already_downloaded} files")
    
    # 並列ダウンロード（進捗表示付き）
    start_time = time.time()
    download_with_progress(urls, downloaded_urls, max_workers=args.threads)
    elapsed_time = time.time() - start_time
    
    print(f"Download completed in {elapsed_time:.2f} seconds!")
    
    # ダウンロード結果の表示
    downloaded_files = sum(1 for _ in Path(ASSETS_DIR).rglob('*') if _.is_file() and _.name != 'downloaded_urls.txt')
    print(f"Total files downloaded: {downloaded_files}")

if __name__ == "__main__":
    main() 