import requests
import json

def test_login():
    url = "http://localhost:8000/api/v1/auth/login"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "username": "user@example.com",
        "password": "string"
    }
    
    try:
        print(f"Testing login at: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, data=data, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_login()
