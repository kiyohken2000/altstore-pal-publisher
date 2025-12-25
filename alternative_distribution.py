#!/usr/bin/env python3
"""
App Store Connect API - Alternative Distribution Package Manager
configure.json から全設定を読み込んで代替配布パッケージIDを取得
"""

import jwt
import time
import requests
import json
import base64
from datetime import datetime, timedelta
from pathlib import Path

class AppStoreConnectAPI:
    def __init__(self, config_path="configure.json"):
        """
        初期化
        
        Args:
            config_path: configure.json のパス
        """
        self.config_path = config_path
        self.config = self.load_config()
        self.base_url = "https://api.appstoreconnect.apple.com/v1"
        
        # configure.json から情報を取得
        self.issuer_id = self.config.get("developer_id", "")
        self.token = self.config.get("security_token", "")
        self.source_url = self.config.get("source_url", "")
        self.email = self.config.get("email", "")
        self.adp_id = self.config.get("adp_id", "")
        self.private_key_path = self.config.get("private_key_path", "")
        
        # トークンからKEY_IDを抽出
        self.key_id = self.extract_key_id_from_token()
        
        self.token_expiry = None
        
        print(f"📁 設定を読み込みました: {config_path}")
        print(f"   Developer ID (Issuer): {self.issuer_id}")
        print(f"   Email: {self.email}")
        print(f"   Source URL: {self.source_url}")
        if self.key_id:
            print(f"   Key ID: {self.key_id}")
        if self.private_key_path:
            print(f"   Private Key: {self.private_key_path}")
            self.check_private_key_file()
        if self.adp_id:
            print(f"   既存のADP ID: {self.adp_id}")
        print()
        
    def check_private_key_file(self):
        """プライベートキーファイルの存在確認"""
        if self.private_key_path and not Path(self.private_key_path).exists():
            print(f"⚠️  警告: プライベートキーファイルが見つかりません: {self.private_key_path}")
            print("   新しいトークンの生成ができません（既存トークンを使用）")
            self.private_key_path = None  # ファイルがない場合は無効化
        elif self.private_key_path:
            print(f"   ✅ プライベートキーファイルを検出")
    
    def load_config(self):
        """configure.json を読み込む"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ エラー: {self.config_path} が見つかりません")
            print("\n新しい configure.json を作成します...")
            default_config = {
                "source_url": "",
                "developer_id": "",
                "email": "",
                "security_token": "",
                "adp_id": "",
                "private_key_path": "./ApiKey_XXXXXXXXXX.p8"
            }
            self.save_config_data(default_config)
            print(f"📝 {self.config_path} を作成しました。設定を入力してください。")
            exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ エラー: JSONの解析に失敗しました: {e}")
            return {}
    
    def save_config(self):
        """configure.json を保存"""
        self.save_config_data(self.config)
    
    def save_config_data(self, data):
        """設定データを保存"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 設定を保存しました: {self.config_path}")
        except Exception as e:
            print(f"❌ 設定の保存に失敗しました: {e}")
    
    def extract_key_id_from_token(self):
        """JWTトークンからKEY_IDを抽出"""
        try:
            if not self.token:
                return ""
            header = jwt.get_unverified_header(self.token)
            return header.get("kid", "")
        except:
            return ""
    
    def check_token_validity(self):
        """既存トークンの有効性をチェック"""
        if not self.token:
            print("❌ トークンが設定されていません")
            return False
            
        try:
            payload = jwt.decode(self.token, options={"verify_signature": False})
            exp_timestamp = payload.get("exp", 0)
            exp_datetime = datetime.fromtimestamp(exp_timestamp)
            
            now = datetime.now()
            if exp_datetime > now:
                remaining = exp_datetime - now
                hours, remainder = divmod(remaining.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                print(f"✅ トークン有効（残り時間: {int(hours)}時間{int(minutes)}分）")
                return True
            else:
                print(f"❌ トークン期限切れ（期限: {exp_datetime}）")
                return False
        except Exception as e:
            print(f"❌ トークンの確認に失敗: {e}")
            return False
    
    def generate_token(self):
        """新しいJWT トークンを生成"""
        if not self.private_key_path:
            print("⚠️  プライベートキーが設定されていないため、既存のトークンを使用します")
            print("   configure.json に 'private_key_path' を追加してください")
            return self.token
        
        if not Path(self.private_key_path).exists():
            print(f"❌ プライベートキーファイルが見つかりません: {self.private_key_path}")
            return self.token
            
        if not self.key_id:
            print("❌ KEY_IDが不明です")
            return None
            
        header = {
            "alg": "ES256",
            "kid": self.key_id,
            "typ": "JWT"
        }
        
        issued_at = int(time.time())
        expiry = issued_at + 1200  # 20分
        
        payload = {
            "iss": self.issuer_id,
            "iat": issued_at,
            "exp": expiry,
            "aud": "appstoreconnect-v1"
        }
        
        try:
            with open(self.private_key_path, 'r') as key_file:
                private_key = key_file.read()
            
            new_token = jwt.encode(payload, private_key, algorithm='ES256', headers=header)
            
            # 新しいトークンを設定に保存
            self.token = new_token
            self.config["security_token"] = new_token
            self.save_config()
            
            print("🔄 新しいトークンを生成しました")
            return new_token
            
        except Exception as e:
            print(f"❌ トークン生成エラー: {e}")
            return None
    
    def get_valid_token(self):
        """有効なトークンを取得"""
        if self.check_token_validity():
            return self.token
        
        # 無効な場合は新規生成を試みる
        if self.private_key_path:
            print("🔄 トークンを更新します...")
            return self.generate_token()
        else:
            print("⚠️  トークンが期限切れです。")
            print("   configure.json に 'private_key_path' を設定してください")
            return self.token  # 期限切れでも試してみる
    
    def make_request(self, method, endpoint, data=None, params=None):
        """APIリクエストを実行"""
        token = self.get_valid_token()
        
        if not token:
            print("❌ 有効なトークンがありません")
            return None
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == 204:
                return {"success": True}
            
            response_data = response.json()
            
            if response.status_code >= 400:
                self.handle_error(response_data)
                return None
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ リクエストエラー: {e}")
            return None
    
    def handle_error(self, error_data):
        """エラーハンドリング"""
        if "errors" in error_data:
            for error in error_data["errors"]:
                print(f"❌ エラー: {error.get('title', 'Unknown error')}")
                print(f"   詳細: {error.get('detail', 'No details')}")
                print(f"   コード: {error.get('code', 'No code')}")
                
                if "not available in your region" in str(error.get('detail', '')):
                    print("\n⚠️  代替配布機能は現在お使いの地域では利用できません。")
                    print("   対応地域: EU圏内")
                    print("   日本での利用はまだ開始されていません。")
    
    def check_availability(self):
        """代替配布機能が利用可能か確認"""
        print("🔍 代替配布機能の利用可能性を確認中...")
        
        result = self.make_request("GET", "/alternativeDistributionDomains")
        
        if result:
            print("✅ 代替配布機能が利用可能です")
            return True
        else:
            print("❌ 代替配布機能は利用できません")
            return False
    
    def get_apps(self):
        """アプリ一覧を取得"""
        print("📱 アプリ一覧を取得中...")
        
        params = {"limit": 200}
        result = self.make_request("GET", "/apps", params=params)
        
        if result and "data" in result:
            apps = []
            print(f"\n   見つかったアプリ: {len(result['data'])}個")
            for app in result["data"]:
                app_info = {
                    "id": app["id"],
                    "name": app["attributes"]["name"],
                    "bundleId": app["attributes"]["bundleId"],
                    "sku": app["attributes"]["sku"]
                }
                apps.append(app_info)
                print(f"   - {app_info['name']} ({app_info['bundleId']})")
                print(f"     ID: {app_info['id']}")
            return apps
        return None
    
    def get_alternative_distribution_packages(self, app_id=None, app_name=None):
        """代替配布パッケージ一覧を取得"""
        if app_name:
            print(f"📦 {app_name} の代替配布パッケージを確認中...")
        else:
            print("📦 代替配布パッケージを取得中...")
        
        endpoint = "/alternativeDistributionPackages"
        params = {}
        
        if app_id:
            params["filter[app]"] = app_id
        
        result = self.make_request("GET", endpoint, params=params)
        
        if result and "data" in result:
            packages = []
            for package in result["data"]:
                package_id = package["id"]
                packages.append(package)
                
                print(f"\n   📦 パッケージID: {package_id}")
                
                # ADP IDを設定に保存（最初のものを保存）
                if not self.config.get("adp_id") and package_id:
                    self.config["adp_id"] = package_id
                    self.save_config()
                    print(f"   💾 ADP IDを configure.json に保存しました")
                
                if "relationships" in package:
                    if "app" in package["relationships"]:
                        print(f"      アプリID: {package['relationships']['app']['data']['id']}")
                    if "appStoreVersion" in package["relationships"]:
                        print(f"      バージョンID: {package['relationships']['appStoreVersion']['data']['id']}")
            
            if not packages:
                print("   代替配布パッケージが見つかりません")
            
            return packages
        return None

def main():
    """メイン実行関数"""
    print("=" * 60)
    print("App Store Connect - 代替配布パッケージ管理ツール")
    print("=" * 60)
    print()
    
    # configure.json から全設定を読み込む（private_key_pathも含む）
    api = AppStoreConnectAPI(config_path="configure.json")
    
    # トークンの状態を確認
    print("=" * 40)
    print("📋 トークン状態確認")
    api.check_token_validity()
    
    # 代替配布機能の利用可能性を確認
    print("\n" + "=" * 40)
    if not api.check_availability():
        print("\n⚠️  注意: 代替配布機能が利用できません。")
        print("以下の確認を行ってください:")
        print("1. アカウントホルダーがAlternative Terms Addendumに同意している")
        print("2. お使いの地域で代替配布が利用可能（現在はEU圏内のみ）")
        print("3. APIキーに適切な権限が付与されている")
        print("\n続行しますか？ (y/n): ", end="")
        if input().lower() != 'y':
            print("終了します")
            return
    
    # アプリ一覧を取得
    print("\n" + "=" * 40)
    apps = api.get_apps()
    
    if apps:
        found_any = False
        # 各アプリの代替配布パッケージを確認
        for app in apps:
            print("\n" + "-" * 40)
            packages = api.get_alternative_distribution_packages(
                app['id'], 
                app['name']
            )
            
            if packages:
                found_any = True
                print(f"✅ {app['name']} の代替配布パッケージIDが見つかりました")
        
        if not found_any:
            print("\n" + "=" * 60)
            print("❌ どのアプリにも代替配布パッケージが見つかりませんでした")
            print("\n考えられる原因:")
            print("1. iOS 16.1 SDK以降でビルドされていない")
            print("2. アプリのステータスが条件を満たしていない")
            print("3. Alternative Termsに同意していない")
            print("4. 地域制限（日本では未対応）")
    
    # 最終確認
    if api.config.get("adp_id"):
        print("\n" + "=" * 60)
        print("✅ Alternative Distribution Package ID:")
        print(f"   {api.config['adp_id']}")
        print("\nこのIDは configure.json に保存されました")
    else:
        print("\n" + "=" * 60)
        print("Alternative Distribution Package IDが取得できませんでした")

if __name__ == "__main__":
    try:
        import jwt
        import requests
    except ImportError:
        print("必要なパッケージをインストールしてください:")
        print("pip install pyjwt cryptography requests")
        exit(1)
    
    main()