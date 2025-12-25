# AltStore PAL API ツール集

このプロジェクトは、AltStore PAL の各種 REST API を操作するためのPythonスクリプト集です。

## 機能

このツールセットでは、以下の AltStore PAL API 機能を利用できます：

* **開発者ID登録** (`register.py`): 開発者IDをAltStore PALに登録し、セキュリティトークンを取得
* **ADP ID自動取得** (`alternative_distribution.py`): App Store Connect APIを使用してAlternative Distribution Package IDを自動取得
* **ADP処理** (`process_adp.py`): Alternative Distribution Package (ADP) の処理をトリガー
* **ADPダウンロード** (`download_adp.py`): ADPのステータス確認と完成したパッケージのダウンロード
* **ソース連携** (`federate.py`): ソースをexplore.alt.storeで検出可能にする

## セットアップ

### 1. 依存ライブラリのインストール

Pythonがインストールされている環境で、以下のコマンドを実行して必要なライブラリをインストールします。

```bash
pip install requests pyjwt cryptography
```

**各ライブラリの用途:**
* `requests`: AltStore PAL API との通信
* `pyjwt`: App Store Connect API の JWT トークン生成（`alternative_distribution.py` 使用時）
* `cryptography`: JWT トークンの暗号化処理（`alternative_distribution.py` 使用時）

### 2. 設定ファイルの作成

`configure.json.example` をコピーして `configure.json` を作成し、必要な情報を記述します。

```bash
cp configureure.json.example configure.json
```

または手動でプロジェクトのルートディレクトリに `configure.json` を作成します。

```json
{
  "source_url": "https://polymorph-distribution.netlify.app/source.json",
  "developer_id": "あなたの開発者ID",
  "email": "your-email@example.com",
  "security_token": "",
  "adp_id": "",
  "private_key_path": "./AuthKey_XXXXXXXXXX.p8"
}
```

**各項目の説明:**
* `source_url`: Federateに使用するソースのURL
* `developer_id`: Apple Developer の Team ID (Issuer ID)
* `email`: 登録に使用するメールアドレス
* `security_token`: register.py実行後に自動で保存されます（手動入力不要）
* `adp_id`: Alternative Distribution Package ID（`alternative_distribution.py` で自動取得可能）
* `private_key_path`: App Store Connect API キーファイルのパス（`alternative_distribution.py` 使用時のみ必要）

## 使い方

各スクリプトを用途に応じて実行します。

### 1. 開発者ID登録（初回のみ）

```bash
python register.py
```

`configure.json` に設定した `developer_id` と `email` を使ってAltStore PALに登録し、セキュリティトークンを取得します。トークンは自動的に `configure.json` に保存されます。

### 2. ADP IDの取得（初回のみ）

#### 方法A: 自動取得（推奨）

```bash
python alternative_distribution.py
```

App Store Connect API を使用してADP IDを自動的に取得します。取得したIDは自動的に `configure.json` に保存されます。

**必要な準備:**
1. [App Store Connect](https://appstoreconnect.apple.com) で API キーを作成
   - ユーザーとアクセス > 統合 > App Store Connect API > キー
   - アクセス権限: **Admin** または **App Manager**
2. ダウンロードした `.p8` ファイルをプロジェクトディレクトリに配置
3. `configure.json` の `private_key_path` にファイルパスを設定
4. `configure.json` の `developer_id` に **Issuer ID** を設定（API キーページに表示）
5. `security_token` にはダウンロードした `.p8` ファイルから生成したJWTトークンを設定（初回は空でOK、スクリプトが自動生成）

詳細: [Creating API Keys for App Store Connect API](https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api)

#### 方法B: 手動取得

App Store Connect の **History** ページから手動でコピーすることも可能です（詳細は下記の「メモ」セクションを参照）。

### 3. ADP処理のトリガー

```bash
python process_adp.py
```

マーケットプレイス通知を待たずに、手動でADP処理を開始します。

### 4. ADPのステータス確認とダウンロード

```bash
python download_adp.py
```

ADP処理の状態を確認し、完成している場合はダウンロードURLが表示されます。

### 5. ソースの連携（Federation）

```bash
python federate.py
```

`configure.json` に設定した `source_url` を explore.alt.store で検出可能にします。

---

**実行後の確認:**
* **Success**: ステータスコード `200` または `201` が返れば成功です。
* **Error**: 設定が正しくない場合やサーバー側に問題がある場合はエラーメッセージが表示されます。

## ファイル構成

* `register.py`: 開発者ID登録スクリプト
* `alternative_distribution.py`: ADP ID自動取得スクリプト（App Store Connect API使用）
* `process_adp.py`: ADP処理トリガースクリプト
* `download_adp.py`: ADPダウンロードスクリプト
* `federate.py`: ソース連携スクリプト
* `configure.json`: 設定ファイル（各種ID、トークン、URLを記述）
* `configure.json.example`: 設定ファイルのサンプル
* `requirements.txt`: 依存ライブラリ
* `README.md`: このドキュメント
* `commands.txt`: よく使うコマンドのコピペ用
* `sample/polymorph/`: サンプルアプリとソース定義ファイル

## メモ

### ADP IDの取得方法

Alternative Distribution Package (ADP) IDは、以下の2つの方法で取得できます。

#### 方法A: 自動取得（推奨）

`alternative_distribution.py` を使用すると、App Store Connect API 経由で自動的にADP IDを取得できます。

```bash
python alternative_distribution.py
```

このスクリプトは以下を自動で行います：
- JWTトークンの生成と有効期限管理
- 代替配布機能の利用可能性チェック
- 登録されている全アプリの検索
- 各アプリのADP IDの取得
- 取得したIDを `configure.json` に自動保存

**前提条件:**
- Apple Developer Programに登録済み
- アプリがiOS 16.1 SDK以降でビルドされている
- 2024年2月8日以降に承認されたアプリバージョン、または「配布準備完了」「配布処理中」「開発者リリース待ち」のステータス
- App Store Connect API キー（Admin または App Manager 権限）
- EU圏内のApple Developer アカウント（日本は未対応）

#### 方法B: 手動取得

App Store Connectから手動で取得することもできます。

**取得手順:**
1. [App Store Connect](https://appstoreconnect.apple.com) にログイン
2. **Apps** から対象のアプリを選択
3. サイドバーの **History** をクリック
4. 適格なアプリバージョンの横にある **Alternative Distribution Package ID** フィールドを確認
5. **Copy** をクリックして ID をコピー
6. コピーしたIDを `configure.json` の `adp_id` に設定

詳細: [Get an Alternative Distribution Package ID](https://developer.apple.com/help/app-store-connect/managing-alternative-distribution/get-an-alternative-distribution-package-id)

### source.json

Federation APIにPostするjsonは[AltStudio](https://altstudio.app)で作成します。ただし、`fediUsername`はAltStudioでは追加できないのでテキストエディタで直接編集します。

### IPAファイルとjsonのホスティング

.ipaファイルとjsonの置き場は自分で用意する必要があります。[Netlify Drop](https://app.netlify.com/drop)がお手軽でした。