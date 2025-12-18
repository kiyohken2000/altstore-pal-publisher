# AltStore Federation Tool

このスクリプトは、指定されたソースURLを AltStore の Federation API (`https://api.altstore.io/federate`) に登録・更新するためのツールです。

## 機能

* 外部ファイル (`config.json`) からソースURLを読み込み。
* AltStore API への POST リクエスト送信。
* エラーハンドリングとレスポンスの表示。

## セットアップ

### 1. 依存ライブラリのインストール

Pythonがインストールされている環境で、以下のコマンドを実行して `requests` ライブラリをインストールします。

```bash
pip install requests
```

### 2. 設定ファイルの作成

プロジェクトのルートディレクトリに `config.json` を作成し、登録したいソースのURLを記述します。

```json
{
  "source_url": "https://your-domain.com/source.json"
}
```

## 使い方

以下のコマンドでスクリプトを実行します。

```bash
python altstore_publisher.py

```

実行後、APIからのレスポンスが表示されます。

* **Success**: ステータスコード `200` または `201` が返れば成功です。
* **Error**: URLが正しくない場合やサーバー側に問題がある場合はエラーメッセージが表示されます。

## ファイル構成

* `main.py`: 実行用メインスクリプト
* `config.json`: 設定ファイル（URLを記述）
* `README.md`: このドキュメント
* `command.txt`: よく使うコマンドのコピペ用
* `sample`: polymorphフォルダをNetlify Dropに丸ごとドラッグドロップしてアップロードした

## メモ

### source.json

Federation APIにPostするjsonは[AltStudio](https://altstudio.app)で作成する。ただし、`fediUsername`はAltStudioでは追加できないのでテキストエディタで直接編集する。

### IPAファイルとjsonのホスティング

.ipaファイルとjsonの置き場は自分で用意する必要があります。[Netlify Drop](https://app.netlify.com/drop)がお手軽でした。