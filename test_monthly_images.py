import requests
import time
import re
from bs4 import BeautifulSoup

BASE_URL = "http://localhost:8080"
IMAGE_TEST_URL = f"{BASE_URL}/ikuoikuo_2005/m/200511.html"  # 問題のあったページ

def test_specific_image():
    """特定の画像（f5bdb4e022c2547ee573dd3e9b086d60.jpg）が正しく表示されるかテスト"""
    print("=== 特定の画像のテスト ===")
    try:
        # ページの取得
        response = requests.get(IMAGE_TEST_URL)
        if response.status_code != 200:
            print(f"❌ ページの取得に失敗: {IMAGE_TEST_URL}")
            return
        
        # 画像パスの抽出
        soup = BeautifulSoup(response.text, 'html.parser')
        target_img = None
        
        for img in soup.find_all('img'):
            if 'f5bdb4e022c2547ee573dd3e9b086d60.jpg' in img.get('src', ''):
                target_img = img
                break
        
        if not target_img:
            print("❌ 対象の画像が見つかりませんでした")
            return
            
        img_url = target_img['src']
        if not img_url.startswith('http'):
            img_url = BASE_URL + img_url
            
        print(f"テスト対象の画像URL: {img_url}")
        
        # 画像へのアクセス
        img_response = requests.get(img_url)
        if img_response.status_code == 200:
            print(f"✅ 画像にアクセス成功: {img_url}")
            print(f"   サイズ: {len(img_response.content)} バイト")
        else:
            print(f"❌ 画像へのアクセスに失敗: {img_url}")
            print(f"   ステータスコード: {img_response.status_code}")
    
    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

def test_all_images():
    """ページ内の全ての画像をテスト"""
    print("\n=== ページ内の全ての画像のテスト ===")
    try:
        # ページの取得
        response = requests.get(IMAGE_TEST_URL)
        if response.status_code != 200:
            print(f"❌ ページの取得に失敗: {IMAGE_TEST_URL}")
            return
        
        # 画像パスの抽出
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')
        
        if not images:
            print("❌ ページ内に画像がありません")
            return
            
        success_count = 0
        fail_count = 0
        
        for img in images:
            if 'src' not in img.attrs:
                continue
                
            img_url = img['src']
            if not img_url.startswith('http'):
                img_url = BASE_URL + img_url
                
            # 画像へのアクセス
            try:
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    success_count += 1
                    print(f"✅ 画像にアクセス成功: {img_url}")
                else:
                    fail_count += 1
                    print(f"❌ 画像へのアクセスに失敗: {img_url}")
                    print(f"   ステータスコード: {img_response.status_code}")
            except Exception as e:
                fail_count += 1
                print(f"❌ エラー発生 ({img_url}): {str(e)}")
        
        print(f"\n合計: {success_count + fail_count}画像中 {success_count}成功、{fail_count}失敗")
    
    except Exception as e:
        print(f"❌ エラー発生: {str(e)}")

if __name__ == "__main__":
    # サーバーが起動するのを待つ
    print("サーバーの起動を待っています...")
    time.sleep(2)
    
    # 特定の画像のテスト
    test_specific_image()
    
    # すべての画像のテスト
    test_all_images() 