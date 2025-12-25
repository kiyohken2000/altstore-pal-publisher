import requests
import json

def load_config():
    with open('configure.json', 'r') as f:
        return json.load(f)

def process_adp():
    config = load_config()

    if not config.get("adp_id"):
        print("エラー: configure.json に adp_id を設定してください")
        return

    api_url = "https://api.altstore.io/adps"

    payload = {
        "adpID": config["adp_id"]
    }

    try:
        response = requests.post(api_url, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code in [200, 201, 202]:
            print(f"\n成功: ADP処理をトリガーしました")
            print("download_adp.py を実行してステータスを確認してください")
        else:
            print(f"エラー: ADP処理のトリガーに失敗しました")

    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    process_adp()
