# AltStore PAL API ツール集

このプロジェクトは、AltStore PAL の各種 REST API を操作するためのPythonスクリプト集です。

## 機能

このツールセットでは、以下の AltStore PAL API 機能を利用できます：

* **開発者ID登録** (`register.py`): 開発者IDをAltStore PALに登録し、セキュリティトークンを取得
* **ADP処理** (`process_adp.py`): Alternative Distribution Package (ADP) の処理をトリガー
* **ADPダウンロード** (`download_adp.py`): ADPのステータス確認と完成したパッケージのダウンロード
* **ソース連携** (`federate.py`): ソースをexplore.alt.storeで検出可能にする

## セットアップ

### 1. 依存ライブラリのインストール

Pythonがインストールされている環境で、以下のコマンドを実行して `requests` ライブラリをインストールします。

```bash
pip install requests
```

### 2. 設定ファイルの作成

`config.json.example` をコピーして `config.json` を作成し、必要な情報を記述します。

```bash
cp config.json.example config.json
```

または手動でプロジェクトのルートディレクトリに `config.json` を作成します。

```json
{
  "source_url": "https://polymorph-distribution.netlify.app/source.json",
  "developer_id": "あなたの開発者ID",
  "email": "your-email@example.com",
  "security_token": "",
  "adp_id": "あなたのADP ID"
}
```

**各項目の説明:**
* `source_url`: Federateに使用するソースのURL
* `developer_id`: Apple Developer の Team ID
* `email`: 登録に使用するメールアドレス
* `security_token`: register.py実行後に自動で保存されます（手動入力不要）
* `adp_id`: App Store ConnectのHistoryから取得したAlternative Distribution Package ID（取得方法は下記の「メモ」セクションを参照）

## 使い方

各スクリプトを用途に応じて実行します。

### 1. 開発者ID登録（初回のみ）

```bash
python register.py
```

`config.json` に設定した `developer_id` と `email` を使ってAltStore PALに登録し、セキュリティトークンを取得します。トークンは自動的に `config.json` に保存されます。

### 2. ADP処理のトリガー

```bash
python process_adp.py
```

マーケットプレイス通知を待たずに、手動でADP処理を開始します。

### 3. ADPのステータス確認とダウンロード

```bash
python download_adp.py
```

ADP処理の状態を確認し、完成している場合はダウンロードURLが表示されます。

### 4. ソースの連携（Federation）

```bash
python federate.py
```

`config.json` に設定した `source_url` を explore.alt.store で検出可能にします。

---

**実行後の確認:**
* **Success**: ステータスコード `200` または `201` が返れば成功です。
* **Error**: 設定が正しくない場合やサーバー側に問題がある場合はエラーメッセージが表示されます。

## ファイル構成

* `register.py`: 開発者ID登録スクリプト
* `process_adp.py`: ADP処理トリガースクリプト
* `download_adp.py`: ADPダウンロードスクリプト
* `federate.py`: ソース連携スクリプト
* `config.json`: 設定ファイル（各種ID、トークン、URLを記述）
* `requirements.txt`: 依存ライブラリ
* `README.md`: このドキュメント
* `commands.txt`: よく使うコマンドのコピペ用
* `sample/polymorph/`: サンプルアプリとソース定義ファイル

## メモ

### ADP IDの取得方法

Alternative Distribution Package (ADP) IDは、App Store Connectから取得します。

**前提条件:**
- Apple Developer Programに登録済み
- アプリがiOS 16.1 SDK以降でビルドされている
- 2024年2月8日以降に承認されたアプリバージョン、または「配布準備完了」「配布処理中」「開発者リリース待ち」のステータス

**取得手順:**
1. [App Store Connect](https://appstoreconnect.apple.com) にログイン
2. **Apps** から対象のアプリを選択
3. サイドバーの **History** をクリック
4. 適格なアプリバージョンの横にある **Alternative Distribution Package ID** フィールドを確認
5. **Copy** をクリックして ID をコピー
6. コピーしたIDを `config.json` の `adp_id` に設定

詳細: [Get an Alternative Distribution Package ID](https://developer.apple.com/help/app-store-connect/managing-alternative-distribution/get-an-alternative-distribution-package-id)

### source.json

Federation APIにPostするjsonは[AltStudio](https://altstudio.app)で作成します。ただし、`fediUsername`はAltStudioでは追加できないのでテキストエディタで直接編集します。

### IPAファイルとjsonのホスティング

.ipaファイルとjsonの置き場は自分で用意する必要があります。[Netlify Drop](https://app.netlify.com/drop)がお手軽でした。