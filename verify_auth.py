import requests
import base64

BASE_URL = "http://localhost:8000" # Adjust if needed

def test_auth():
    # Test unauthorized access
    print("Testing unauthorized access to /dashboard/metrics...")
    res = requests.get(f"{BASE_URL}/dashboard/metrics")
    print(f"Status: {res.status_code} (Expected 401)")

    # Test login with dummy (but formatted) credentials
    # Note: This will fail verification unless real credentials are used
    print("\nTesting login endpoint...")
    login_data = {"email": "test@example.com", "password": "password123"}
    res = requests.post(f"{BASE_URL}/login", json=login_data)
    print(f"Status: {res.status_code}")
    print(f"Body: {res.json()}")

if __name__ == "__main__":
    test_auth()
