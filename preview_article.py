#!/usr/bin/env python3
import os
import sys
import webbrowser
from pathlib import Path
import argparse
import random

# ローカルHTMLファイルのディレクトリ
LOCAL_HTML_DIR = "local_html"

def find_article_files():
    """記事ファイルを検索する"""
    local_html = Path(LOCAL_HTML_DIR)
    
    # local_htmlディレクトリが存在しない場合はエラー
    if not local_html.exists():
        print(f"Error: {LOCAL_HTML_DIR} directory not found.")
        print("Please run localize_html.py first to create local HTML files.")
        return []
    
    # ikuoikuo_2005ディレクトリ内のHTMLファイルを検索（アーカイブページを除外）
    article_files = []
    
    # 記事ページのみを抽出（アーカイブ、カテゴリ、画像一覧などは除外）
    for html_file in list(local_html.glob("ikuoikuo_2005/*.html")):
        file_name = html_file.name.lower()
        # アーカイブページやカテゴリページなどを除外
        if not any(x in file_name for x in ['arcv', 'category', 'images', 'follower']):
            article_files.append(html_file)
    
    return article_files

def preview_article(article_path=None):
    """指定された記事ファイルをブラウザで開く"""
    article_files = find_article_files()
    
    if not article_files:
        print("No article files found in the local_html directory.")
        print("Make sure you have run both download_assets.py and localize_html.py.")
        return False
    
    # 表示する記事ファイルを決定
    target_article = None
    
    if article_path:
        # 指定されたパスの記事を検索
        for article in article_files:
            if article_path in str(article):
                target_article = article
                break
        
        if not target_article:
            print(f"Article with path '{article_path}' not found.")
            print("Available articles:")
            for i, article in enumerate(sorted(article_files)[:10]):
                print(f"  {i+1}. {article.relative_to(LOCAL_HTML_DIR)}")
            if len(article_files) > 10:
                print(f"  ... and {len(article_files) - 10} more.")
            return False
    else:
        # ランダムに記事を選択
        target_article = random.choice(article_files)
    
    # 記事ファイルのURIを作成
    file_uri = f"file://{os.path.abspath(target_article)}"
    
    print(f"Opening article: {target_article.relative_to(LOCAL_HTML_DIR)}")
    print(f"URI: {file_uri}")
    
    # ブラウザで開く
    webbrowser.open(file_uri)
    return True

def main():
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='Preview a blog article in browser')
    parser.add_argument('article_path', nargs='?', help='Part of the article path or filename (optional)')
    parser.add_argument('--list', action='store_true', help='List available articles')
    args = parser.parse_args()
    
    # 記事一覧を表示
    if args.list:
        article_files = find_article_files()
        if article_files:
            sorted_articles = sorted(article_files)
            print(f"Found {len(article_files)} articles:")
            for i, article in enumerate(sorted_articles[:20]):
                print(f"  {i+1}. {article.relative_to(LOCAL_HTML_DIR)}")
            if len(article_files) > 20:
                print(f"  ... and {len(article_files) - 20} more.")
        else:
            print("No article files found in the local_html directory.")
        return
    
    # 記事をプレビュー
    preview_article(args.article_path)

if __name__ == "__main__":
    main() 