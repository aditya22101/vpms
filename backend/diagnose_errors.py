"""
Diagnostic script to find why operations are failing
Run this while backend is running
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_connection():
    """Test if backend is reachable"""
    try:
        response = requests.get("http://localhost:5000/", timeout=2)
        print("✅ Backend is running")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend is NOT running!")
        print("   Start it with: python run.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_admin_login():
    """Test admin login"""
    try:
        response = requests.post(
            f"{BASE_URL}/admin/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print("✅ Admin login works")
            return token
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin login error: {str(e)}")
        return None

def test_create_lot(token):
    """Test creating parking lot"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "prime_location_name": "Diagnostic Test Lot",
            "address": "123 Test Street",
            "pin_code": "123456",
            "price": 50.0,
            "number_of_spots": 5
        }
        response = requests.post(
            f"{BASE_URL}/admin/parking-lots",
            json=data,
            headers=headers,
            timeout=5
        )
        print(f"\nCreate Lot Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 201:
            print("✅ Create parking lot works")
            result = response.json()
            return result.get('id') or (result.get('lot', {}) if isinstance(result, dict) else {}).get('id')
        else:
            print(f"❌ Create parking lot failed")
            return None
    except Exception as e:
        print(f"❌ Create lot error: {str(e)}")
        return None

def test_book_parking(user_token, lot_id):
    """Test booking parking"""
    try:
        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.post(
            f"{BASE_URL}/user/book-parking",
            json={"lot_id": lot_id},
            headers=headers,
            timeout=5
        )
        print(f"\nBook Parking Status: {response.status_code}")
        print(f"Response: {response.text[:300]}")
        
        if response.status_code == 201:
            print("✅ Book parking works")
            return True
        else:
            print(f"❌ Book parking failed")
            return False
    except Exception as e:
        print(f"❌ Book parking error: {str(e)}")
        return False

def main():
    print("=" * 70)
    print("DIAGNOSING ERRORS")
    print("=" * 70)
    
    # Test 1: Connection
    if not test_connection():
        return
    
    # Test 2: Admin Login
    token = test_admin_login()
    if not token:
        print("\n❌ Cannot proceed without admin token")
        return
    
    # Test 3: Create Lot
    lot_id = test_create_lot(token)
    if not lot_id:
        print("\n❌ Cannot proceed without parking lot")
        return
    
    # Test 4: User Registration/Login
    print("\n[4] Testing user registration...")
    try:
        # Try to register
        response = requests.post(
            f"{BASE_URL}/user/register",
            json={
                "username": "testuser_diag",
                "email": "testdiag@example.com",
                "password": "test123"
            },
            timeout=5
        )
        if response.status_code not in [201, 400]:  # 400 = already exists, that's OK
            print(f"   ⚠️  Registration: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Registration error: {str(e)}")
    
    # Try to login
    try:
        response = requests.post(
            f"{BASE_URL}/user/login",
            json={"username": "testuser_diag", "password": "test123"},
            timeout=5
        )
        if response.status_code == 200:
            user_token = response.json().get('token')
            print("✅ User login works")
            
            # Test booking
            test_book_parking(user_token, lot_id)
        else:
            print(f"❌ User login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User login error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    print("\nCheck the errors above to see what's failing.")
    print("The actual error messages will tell you exactly what's wrong.")

if __name__ == "__main__":
    main()

