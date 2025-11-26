"""
Debug script to test backend routes
Run this to check if routes are working
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_admin_login():
    """Test admin login"""
    print("\n=== Testing Admin Login ===")
    response = requests.post(
        f"{BASE_URL}/admin/login",
        json={"username": "admin", "password": "admin123"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    if response.status_code == 200:
        return response.json().get('token')
    return None

def test_create_parking_lot(token):
    """Test creating a parking lot"""
    print("\n=== Testing Create Parking Lot ===")
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "prime_location_name": "Test Parking",
        "address": "123 Test Street",
        "pin_code": "123456",
        "price": 50.0,
        "number_of_spots": 10
    }
    response = requests.post(
        f"{BASE_URL}/admin/parking-lots",
        json=data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 201

def test_get_stats(token):
    """Test getting stats"""
    print("\n=== Testing Get Stats ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/stats",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_get_recent_activity(token):
    """Test getting recent activity"""
    print("\n=== Testing Get Recent Activity ===")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/recent-activity",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

if __name__ == "__main__":
    print("VPMS Backend Debug Test")
    print("=" * 50)
    
    # Test admin login
    token = test_admin_login()
    
    if token:
        # Test other endpoints
        test_get_stats(token)
        test_get_recent_activity(token)
        test_create_parking_lot(token)
        print("\n✅ All tests completed!")
    else:
        print("\n❌ Login failed. Check admin credentials.")



