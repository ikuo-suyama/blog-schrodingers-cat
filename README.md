# アセットダウンローダー README

## 概要
HTMLファイルから抽出したCSS, JavaScript, 画像ファイルをドメイン構造を維持したままダウンロードするPythonスクリプトです。

## 使い方
\`\`\`bash
# 基本実行
python download_assets.py

# スレッド数を指定して実行
python download_assets.py --threads 20

# 失敗したダウンロードを再試行
python download_assets.py --retry
\`\`\`

## 機能
- ドメイン構造を維持したディレクトリ作成
- 並列ダウンロードによる高速化
- プログレスバー表示
- レジューム機能（中断しても続きから再開可能）
- 既存ファイルのスキップ

