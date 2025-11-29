import requests
import json

def test_critique():
    url = "http://127.0.0.1:8000/critique"
    payload = {
        "text": "He was very angry and said loudly that he wanted to leave."
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("Status Code:", response.status_code)
        print("Critique:", data.get("critique"))
        print("Sources:", data.get("sources"))
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_critique()
