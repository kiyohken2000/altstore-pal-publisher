import requests
import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def register_developer():
    config = load_config()

    if not config.get("developer_id") or not config.get("email"):
        print("エラー: config.json に developer_id と email を設定してください")
        return

    api_url = "https://api.altstore.io/register"

    payload = {
        "developerID": config["developer_id"],
        "email": config["email"]
    }

    try:
        response = requests.post(api_url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code in [200, 201]:
            data = response.json()
            if "token" in data:
                config["security_token"] = data["token"]
                save_config(config)
                print(f"\n成功: セキュリティトークンを config.json に保存しました")
                if "expiration" in data:
                    print(f"トークン有効期限: {data['expiration']}")
        else:
            print(f"エラー: 登録に失敗しました")

    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    register_developer()
