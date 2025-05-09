#!/usr/bin/env python3
import os
import urllib.parse
import requests
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
from tqdm import tqdm

# アセットを保存するベースディレクトリ
ASSETS_DIR = "assets"
# ダウンロード済みURLを記録するファイル
DOWNLOADED_FILE = os.path.join(ASSETS_DIR, "downloaded_urls.txt")

def load_asset_urls():
    """アセットリストファイルからURLを読み込む"""
    asset_file = os.path.join(ASSETS_DIR, "normalized_all_assets.txt")
    
    if not os.path.exists(asset_file):
        asset_file = os.path.join(ASSETS_DIR, "all_assets.txt")
        if not os.path.exists(asset_file):
            print(f"Error: Asset list file '{asset_file}' not found.")
            print("Please run list_assets.py first to generate asset lists.")
            return set()
    
    with open(asset_file, 'r', encoding='utf-8') as f:
        urls = set(line.strip() for line in f if line.strip())
    
    print(f"Loaded {len(urls)} URLs from {asset_file}")
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(normalized_url, headers=headers, timeout=10, stream=True)
        
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

def main():
    import argparse
    
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Download assets from asset list files')
    parser.add_argument('--threads', type=int, default=10, help='Number of download threads (default: 10)')
    parser.add_argument('--retry', action='store_true', help='Retry failed downloads')
    parser.add_argument('--css-only', action='store_true', help='Download only CSS files')
    parser.add_argument('--js-only', action='store_true', help='Download only JS files')
    args = parser.parse_args()
    
    # アセット用ディレクトリを作成
    os.makedirs(ASSETS_DIR, exist_ok=True)
    
    # ダウンロード済みURLのリストを読み込む
    downloaded_urls = load_downloaded_urls()
    if args.retry:
        downloaded_urls = set()  # リトライモードの場合は全てダウンロード
    
    # アセットリストからURLを読み込む
    if args.css_only:
        asset_file = os.path.join(ASSETS_DIR, "normalized_css_files.txt")
        if not os.path.exists(asset_file):
            asset_file = os.path.join(ASSETS_DIR, "css_files.txt")
        with open(asset_file, 'r', encoding='utf-8') as f:
            urls = set(line.strip() for line in f if line.strip())
        print(f"Loaded {len(urls)} CSS URLs from {asset_file}")
    elif args.js_only:
        asset_file = os.path.join(ASSETS_DIR, "normalized_js_files.txt")
        if not os.path.exists(asset_file):
            asset_file = os.path.join(ASSETS_DIR, "js_files.txt")
        with open(asset_file, 'r', encoding='utf-8') as f:
            urls = set(line.strip() for line in f if line.strip())
        print(f"Loaded {len(urls)} JS URLs from {asset_file}")
    else:
        urls = load_asset_urls()
    
    # ダウンロード済みファイル数
    already_downloaded = sum(1 for url in urls if normalize_url(url) in downloaded_urls)
    print(f"Already downloaded: {already_downloaded} files")
    print(f"Remaining to download: {len(urls) - already_downloaded} files")
    
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