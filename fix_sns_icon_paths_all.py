#!/usr/bin/env python3
import os
import re
from pathlib import Path
import glob

# ディレクトリパス
HTML_DIRS = [
    "local_html/ikuoikuo_2005/m",  # 月別アーカイブ
    "local_html/ikuoikuo_2005/e"   # 記事
]

def fix_sns_icon_paths(html_content):
    """SNSアイコン画像のパスを修正する"""
    # 問題のパターンを修正
    patterns = [
        (r'<img alt="X" height="20" src="/assets/blogimg\.goo\.ne\.jp/user_image/path/x_logo\.png" width="20"/>', 
         r'<img alt="X" height="20" src="/assets/i.xgoo.jp/img/icon/x_logo.png" width="20"/>'),
        
        (r'<img alt="Facebookでシェアする" height="20" src="//u\.xgoo\.jp/img/sns/button/facebook\.png" width="20"/>', 
         r'<img alt="Facebookでシェアする" height="20" src="/assets/u.xgoo.jp/img/sns/button/facebook.png" width="20"/>'),
        
        (r'<img alt="はてなブックマークに追加する" height="20" src="//u\.xgoo\.jp/img/sns/button/hatena\.png" width="20"/>', 
         r'<img alt="はてなブックマークに追加する" height="20" src="/assets/u.xgoo.jp/img/sns/button/hatena.png" width="20"/>'),
        
        (r'<img alt="LINEでシェアする" height="20" src="//u\.xgoo\.jp/img/sns/button/line\.png" width="20"/>', 
         r'<img alt="LINEでシェアする" height="20" src="/assets/u.xgoo.jp/img/sns/button/line.png" width="20"/>')
    ]
    
    modified_content = html_content
    total_changes = 0
    
    for pattern, replacement in patterns:
        modified_content, count = re.subn(pattern, replacement, modified_content)
        total_changes += count
    
    return modified_content, total_changes

def process_html_files():
    """全てのHTMLファイルを処理する"""
    processed_files = 0
    modified_files = 0
    total_changes = 0
    
    # HTML ファイルを検索
    html_files = []
    for dir_path in HTML_DIRS:
        found_files = glob.glob(f"{dir_path}/**/*.html", recursive=True)
        html_files.extend(found_files)
        print(f"{dir_path} ディレクトリ内に {len(found_files)} ファイルを発見")
    
    total_files = len(html_files)
    
    print(f"合計 {total_files} ファイルを処理します...")
    
    for file_path in html_files:
        processed_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # パスを修正
            modified_content, changes = fix_sns_icon_paths(content)
            
            # 変更があれば保存
            if changes > 0:
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(modified_content)
                
                modified_files += 1
                total_changes += changes
                print(f"修正: {file_path} ({changes}箇所)")
        except Exception as e:
            print(f"エラー: {file_path} の処理中に問題が発生しました - {str(e)}")
    
    print(f"処理完了: {total_files}ファイル中{modified_files}ファイルを修正しました（合計{total_changes}箇所）")

if __name__ == "__main__":
    process_html_files() 