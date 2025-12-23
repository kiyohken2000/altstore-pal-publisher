import requests
import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def download_adp():
    config = load_config()

    if not config.get("adp_id"):
        print("エラー: config.json に adp_id を設定してください")
        return

    adp_id = config["adp_id"]
    api_url = f"https://api.altstore.io/adps/{adp_id}"

    try:
        response = requests.get(api_url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            if "status" in data:
                print(f"\nADPステータス: {data['status']}")
            if "downloadURL" in data:
                print(f"ダウンロードURL: {data['downloadURL']}")
                print("\n✓ ADPの準備ができています")
            else:
                print("\n処理中... まだダウンロードURLは利用できません")
        else:
            print(f"エラー: ADPの取得に失敗しました")

    except Exception as e:
        print(f"エラー: {e}")

if __name__ == "__main__":
    download_adp()
