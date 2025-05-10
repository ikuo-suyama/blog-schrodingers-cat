#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path
import urllib.parse

# 入力と出力のディレクトリ
RAW_HTML_DIR = "raw_html"
LOCAL_HTML_DIR = "local_html"
ASSETS_DIR = "assets"

def load_asset_urls():
    """アセットリストファイルからURLを読み込む"""
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
    """URLを正規化する"""
    if url.startswith('//'):
        return f'https:{url}'
    elif url.startswith('/'):
        return f'https://blog.goo.ne.jp{url}'
    elif not url.startswith(('http://', 'https://')):
        return url
    return url

def is_asset_url(url):
    """URLがアセット（CSS、JS、画像など）であるかどうかを判定"""
    # 拡張子を取得
    _, ext = os.path.splitext(url.split('?')[0])
    
    # アセット判定用の拡張子リスト
    asset_extensions = [
        '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.ico',
        '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.webm', '.mp3', '.wav'
    ]
    
    return ext.lower() in asset_extensions

def create_url_mapping(asset_urls):
    """URLとアセットパスのマッピングを作成"""
    url_mapping = {}
    
    for url in asset_urls:
        normalized_url = normalize_url(url)
        parsed_url = urllib.parse.urlparse(normalized_url)
        
        # 元のURL（正規化済み）と新しい相対パスのマッピング
        asset_path = f"/assets/{parsed_url.netloc}{parsed_url.path}"
        
        # クエリパラメータがある場合はそのまま維持
        if parsed_url.query:
            asset_path += f"?{parsed_url.query}"
        
        url_mapping[url] = asset_path
        
        # 正規化されたURLも同じパスにマッピング
        url_mapping[normalized_url] = asset_path
    
    return url_mapping

def process_html_files(url_mapping):
    """HTMLファイルを処理して相対パスに変換"""
    # 出力ディレクトリをクリアして作成
    if os.path.exists(LOCAL_HTML_DIR):
        shutil.rmtree(LOCAL_HTML_DIR)
    os.makedirs(LOCAL_HTML_DIR, exist_ok=True)
    
    # raw_htmlディレクトリからすべてのHTMLファイルを取得
    html_files = list(Path(RAW_HTML_DIR).glob("**/*.html"))
    
    if not html_files:
        print("No HTML files found in raw_html directory!")
        return
    
    print(f"Processing {len(html_files)} HTML files...")
    
    # URLパターンのリスト（href属性だけは特別扱い）
    url_patterns = [
        # src属性（JS、画像に使用）
        (r'src=["\']([^"\']+)["\']', 'src'),
        # background属性
        (r'background=["\']([^"\']+)["\']', 'background'),
        # CSS内のurl()
        (r'url\(["\']?([^"\'\)]+)["\']?\)', 'url'),
        # content属性（画像URLが入っていることがある）
        (r'content=["\']([^"\']+)["\']', 'content'),
    ]
    
    # href属性を特別に扱うパターン
    href_pattern = r'href=["\']([^"\']+)["\']'
    
    # 処理されたファイル数
    processed_files = 0
    replaced_urls = 0
    
    for html_file in html_files:
        with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 元のファイル名を取得
        file_name = os.path.basename(html_file)
        
        # 出力ファイルパス
        output_file = os.path.join(LOCAL_HTML_DIR, file_name)
        
        # href属性を処理（アセットとナビゲーションリンクを区別）
        href_matches = re.finditer(href_pattern, content)
        for match in href_matches:
            original_url = match.group(1)
            
            # 内部リンク（#で始まる）やjavascript、mailto: は置換しない
            if original_url.startswith(('#', 'javascript:', 'mailto:')):
                continue
            
            normalized_url = normalize_url(original_url)
            
            # アセットURLの場合のみ置換（CSS など）
            if is_asset_url(original_url) or is_asset_url(normalized_url):
                if original_url in url_mapping:
                    new_url = url_mapping[original_url]
                    old_attr = f'href="{original_url}"'
                    new_attr = f'href="{new_url}"'
                    content = content.replace(old_attr, new_attr)
                    replaced_urls += 1
                elif normalized_url in url_mapping:
                    new_url = url_mapping[normalized_url]
                    old_attr = f'href="{original_url}"'
                    new_attr = f'href="{new_url}"'
                    content = content.replace(old_attr, new_attr)
                    replaced_urls += 1
        
        # その他のアセット属性（src, background, url(), content）を処理
        for pattern, attr_type in url_patterns:
            # マッチするすべてのURLを見つける
            matches = re.finditer(pattern, content)
            
            # 各マッチを処理
            for match in matches:
                original_url = match.group(1)
                
                # 内部リンク（#で始まる）やjavascriptは置換しない
                if original_url.startswith(('#', 'javascript:', 'mailto:')):
                    continue
                
                normalized_url = normalize_url(original_url)
                
                # URLがマッピングに存在するか確認
                if original_url in url_mapping:
                    new_url = url_mapping[original_url]
                    # 元のURLを新しいURLに置換
                    old_attr = f'{attr_type}="{original_url}"' if attr_type != 'url' else f'url({original_url})'
                    new_attr = f'{attr_type}="{new_url}"' if attr_type != 'url' else f'url({new_url})'
                    content = content.replace(old_attr, new_attr)
                    replaced_urls += 1
                
                # 正規化されたURLがマッピングに存在するか確認
                elif normalized_url in url_mapping:
                    new_url = url_mapping[normalized_url]
                    # 元のURLを新しいURLに置換
                    old_attr = f'{attr_type}="{original_url}"' if attr_type != 'url' else f'url({original_url})'
                    new_attr = f'{attr_type}="{new_url}"' if attr_type != 'url' else f'url({new_url})'
                    content = content.replace(old_attr, new_attr)
                    replaced_urls += 1
        
        # ファイルを保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        processed_files += 1
        
        # 進捗表示
        if processed_files % 10 == 0:
            print(f"Processed {processed_files}/{len(html_files)} files...")
    
    # サブディレクトリをコピー
    for subdir in os.listdir(RAW_HTML_DIR):
        src_dir = os.path.join(RAW_HTML_DIR, subdir)
        if os.path.isdir(src_dir):
            dst_dir = os.path.join(LOCAL_HTML_DIR, subdir)
            if not os.path.exists(dst_dir):
                shutil.copytree(src_dir, dst_dir)
    
    print(f"Completed processing {processed_files} HTML files.")
    print(f"Replaced {replaced_urls} URLs with asset paths.")
    print(f"HTML files saved to {LOCAL_HTML_DIR}/")

def main():
    # アセットURLのリストを読み込む
    asset_urls = load_asset_urls()
    if not asset_urls:
        return
    
    # URLとアセットパスのマッピングを作成
    url_mapping = create_url_mapping(asset_urls)
    print(f"Created URL mapping for {len(url_mapping)} URLs.")
    
    # HTMLファイルを処理
    process_html_files(url_mapping)

if __name__ == "__main__":
    main() 