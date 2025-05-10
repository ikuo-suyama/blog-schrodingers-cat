#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup
from pathlib import Path

# ディレクトリパス
LOCAL_HTML_DIR = "local_html"

def fix_backnumber_links(html_content):
    """バックナンバーリンクに.htmlを追加する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # バックナンバーセクションを見つける
    backnumber_heading = None
    for heading in soup.find_all('h4'):
        if heading.text == 'バックナンバー':
            backnumber_heading = heading
            break
    
    if not backnumber_heading:
        return html_content, 0
    
    # バックナンバーセクションの下にあるリンクを修正
    module_body = backnumber_heading.find_next_sibling('div', class_='module-body')
    
    if not module_body:
        return html_content, 0
    
    links_modified = 0
    
    # すべてのリンクをチェック
    for link in module_body.find_all('a', href=True):
        href = link['href']
        
        # リンクが /ikuoikuo_2005/m/YYYYMM 形式かチェック
        match = re.search(r'^(/ikuoikuo_2005/m/\d{6})$', href)
        if match:
            # .html を追加
            new_href = href + '.html'
            link['href'] = new_href
            links_modified += 1
            print(f"  修正: {href} -> {new_href}")
    
    return str(soup), links_modified

def process_html_files():
    """すべてのHTMLファイルを処理"""
    total_files = 0
    modified_files = 0
    total_links_modified = 0
    
    print(f"HTMLファイルの検索を開始しています...")
    html_files = []
    for root, _, files in os.walk(LOCAL_HTML_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"全部で{len(html_files)}個のHTMLファイルが見つかりました")
    
    for file_path in html_files:
        total_files += 1
        if total_files % 100 == 0:
            print(f"進捗: {total_files}/{len(html_files)}ファイルを処理中...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # バックナンバーリンクを修正
            modified_content, links_modified = fix_backnumber_links(html_content)
            
            if links_modified > 0:
                # 変更があった場合のみファイルを書き込む
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                modified_files += 1
                total_links_modified += links_modified
                print(f"ファイル修正: {file_path} ({links_modified}リンク修正)")
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    print(f"処理完了: {total_files}ファイル中{modified_files}ファイルを修正")
    print(f"合計{total_links_modified}リンクを修正しました")

if __name__ == "__main__":
    process_html_files() 