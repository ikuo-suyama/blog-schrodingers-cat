# アセットダウンローダー README

## 概要
HTMLファイルから抽出したCSS, JavaScript, 画像ファイルをドメイン構造を維持したままダウンロードし、ローカルでブラウジングできるようにするツールセットです。

## 使い方

### 1. アセットのダウンロード

```bash
# 基本実行
python download_assets.py

# スレッド数を指定して実行
python download_assets.py --threads 20

# 失敗したダウンロードを再試行
python download_assets.py --retry
```

### 2. HTML内のURLをローカルパスに変換

```bash
# HTMLファイルのURL参照をローカルファイルへの参照に変換
python localize_html.py
```

### 3. ブログ記事のプレビュー

```bash
# ランダムな記事をブラウザで開く
python preview_article.py

# 特定のキーワードを含む記事を開く
python preview_article.py キーワード

# 利用可能な記事一覧を表示
python preview_article.py --list
```

## 機能

### download_assets.py

- ドメイン構造を維持したディレクトリ作成
- 並列ダウンロードによる高速化
- プログレスバー表示
- レジューム機能（中断しても続きから再開可能）
- 既存ファイルのスキップ

### localize_html.py

- HTML内のURL参照をローカルパスに変換
- 相対パスとルート相対パスの適切な処理
- 複雑なURLパターンの処理（クエリパラメータ、アンカーなど）
- すべてのHTMLファイルの一括処理

### preview_article.py

- ブログ記事をブラウザで簡単にプレビュー
- ランダム記事表示機能
- キーワード検索による記事選択
- 記事一覧表示機能

## ディレクトリ構造

```
project/
  ├── raw_html/           # 元のHTMLファイル
  ├── assets/             # ダウンロードされたアセット
  │   ├── blog.goo.ne.jp/
  │   ├── blogimg.goo.ne.jp/
  │   └── ...
  ├── local_html/         # ローカル参照に変換されたHTMLファイル
  ├── download_assets.py  # アセットダウンロードスクリプト
  ├── localize_html.py    # HTML変換スクリプト
  └── preview_article.py  # 記事プレビュースクリプト
```

