# 英単語のスクレイピング

## 使い方
１．main.pyを起動
２．UIに必要項目を入力
３．検索ボタンをクリック
４．main.pyと同じフォルダにファイルが出力される

## ディレクトリ構成
### View
フロントの制御を担当
eelで仕様するHTMLファイルとJSファイルを管理
js/myscript.js：バックエンドとやりとり

### controller
フロントとバックエンドの繋ぎを担当
desktop.py：eelの画面表示
bridge.py：viewから受け取り、modelでの処理結果を返すための橋渡し

### model
バックエンドを担当
各制御のクラスを提供する
