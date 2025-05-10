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

def fix_additional_icon_paths(html_content):
    """追加のアイコン（ナビゲーション、お知らせ、プロフィール）画像のパスを修正する"""
    
    # 問題のパターンを修正
    patterns = [
        # ナビゲーションメニューのアイコン
        (r'<img alt="" src="/assets/goo\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sns/goo.svg"/>'),
        
        (r'<img alt="" src="/assets/dpoint\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/dpoint.svg"/>'),
        
        (r'<img alt="" src="/assets/mail\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/mail.svg"/>'),
        
        (r'<img alt="" src="/assets/news\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/news.svg"/>'),
        
        (r'<img alt="" src="/assets/dictionary\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/dictionary.svg"/>'),
        
        (r'<img alt="" src="/assets/oshiete\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/oshiete.svg"/>'),
        
        (r'<img alt="" src="/assets/blog\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/blog.svg"/>'),
        
        (r'<img alt="" src="/assets/house\.svg"/>', 
         r'<img alt="" src="/assets/u.xgoo.jp/img/sv/house.svg"/>'),
        
        # お知らせセクションのアイコン - 正しいパスはimg/emojiではなくimg_emoji
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/star\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img_emoji/star.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/m_0148\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img_emoji/m_0148.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/m_0146\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img_emoji/m_0146.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/m_0001\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img_emoji/m_0001.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/m_0244\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img_emoji/m_0244.gif"'),
        
        # プロフィールの画像
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/d7558152496caf3ef82cd5ff1730ee3f\.jpg"', 
         r'src="/assets/blogimg.goo.ne.jp/user_photo/bc/d7558152496caf3ef82cd5ff1730ee3f.jpg"'),
        
        # ブログ管理関連アイコン
        (r'src="/assets/blogimg\.goo\.ne\.jp/img/static/blog/mod_pen\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img/static/blog/mod_pen.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/twitter_logo\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img/portal/misc/side/twitter_logo.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/mod_newmake\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img/static/blog/mod_newmake.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/btn_rss\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img/static/blog/btn_rss.gif"'),
        
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/icon_poweredbygooblog\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img/static/blog/icon_poweredbygooblog.gif"'),
        
        # グローバルヘッダーのアイコン
        (r'src="/assets/blogimg\.goo\.ne\.jp/user_image/path/mod_global_header_goo_logo\.gif"', 
         r'src="/assets/blogimg.goo.ne.jp/img/static/blog/mod_global_header_goo_logo.gif"')
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
            modified_content, changes = fix_additional_icon_paths(content)
            
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