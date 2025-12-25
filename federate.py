import requests
import json

def load_config():
    with open('configure.json', 'r') as f:
        return json.load(f)

def federate_altstore():
    config = load_config()
    api_url = "https://api.altstore.io/federate"
    
    payload = {
        "source": config["source_url"]
    }
    
    response = requests.post(api_url, json=payload)
    print(f"Status: {response.status_code}, Body: {response.text}")

if __name__ == "__main__":
    federate_altstore()