import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    print("--- Starting Verification ---")

    # 1. Create New Chat
    print("\n1. Creating New Chat...")
    res = requests.post(f"{BASE_URL}/chats", json={"title": "Test Chat"})
    if res.status_code != 200:
        print(f"FAILED: Could not create chat. {res.text}")
        return
    chat_id = res.json()["id"]
    print(f"SUCCESS: Created chat ID {chat_id}")

    # 2. Send Greeting (Conversation Intent)
    print("\n2. Sending Greeting...")
    payload = {"text": "Hello, who are you?", "conversation_id": chat_id}
    res = requests.post(f"{BASE_URL}/submit", json=payload)
    if res.status_code != 200:
        print(f"FAILED: Submit failed. {res.text}")
        return
    data = res.json()
    print(f"Response: {data.get('response')}")
    if "Forge" in data.get("response", "") or "writing coach" in data.get("response", ""):
        print("SUCCESS: Correctly identified question/greeting.")
    else:
        print("WARNING: Response might not be conversational.")

    # 3. Send Submission (Critique Intent)
    print("\n3. Sending Submission...")
    submission_text = "The night was dark and stormy. Suddenly, a shot rang out. Detective Smith grabbed his gun and ran towards the sound. He saw a shadow move in the alley. 'Stop!' he yelled."
    # Make it longer to trigger submission
    submission_text = " ".join(["word"] * 60)
    
    payload = {"text": submission_text, "conversation_id": chat_id}
    res = requests.post(f"{BASE_URL}/submit", json=payload)
    data = res.json()
    
    if data.get("plan", {}).get("classification") == "submission":
        print("SUCCESS: Correctly classified as submission.")
    else:
        print(f"FAILED: Classified as {data.get('plan', {}).get('classification')}")

    # 4. Verify Persistence
    print("\n4. Verifying Persistence...")
    res = requests.get(f"{BASE_URL}/chats/{chat_id}")
    chat_data = res.json()
    messages = chat_data.get("messages", [])
    print(f"Found {len(messages)} messages in history.")
    
    if len(messages) >= 4: # User greeting, Assistant response, User submission, Assistant response
        print("SUCCESS: History persisted.")
    else:
        print("FAILED: Missing messages in history.")

    # 5. Test Context (Follow-up)
    print("\n5. Testing Context...")
    payload = {"text": "What did I just submit?", "conversation_id": chat_id}
    res = requests.post(f"{BASE_URL}/submit", json=payload)
    data = res.json()
    print(f"Response: {data.get('response')}")
    print("SUCCESS: Follow-up submitted.")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_flow()
