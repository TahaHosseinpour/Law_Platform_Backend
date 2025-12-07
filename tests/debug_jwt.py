"""Debug JWT token issue"""
import httpx
import asyncio
from jose import jwt

BASE_URL = "http://localhost:8000"
JWT_SECRET = "your-super-secret-key-please-change-this-in-production-09876543210"
JWT_ALGORITHM = "HS256"

async def debug():
    async with httpx.AsyncClient() as client:
        # Register
        user_data = {
            "email": "debug@test.com",
            "fullName": "Debug User",
            "password": "DebugPass123!",
            "role": "USER"
        }

        reg_response = await client.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Register: {reg_response.status_code}")
        if reg_response.status_code == 400:
            print("User exists, trying login...")

        # Login
        login_data = {"email": user_data["email"], "password": user_data["password"]}
        login_response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login: {login_response.status_code}")
        print(f"Login Response: {login_response.json()}")

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            print(f"\nToken: {token[:50]}...")

            # Decode token locally
            try:
                payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
                print(f"\nDecoded payload: {payload}")
                print(f"Sub type: {type(payload.get('sub'))}")
                print(f"Sub value: {payload.get('sub')}")
            except Exception as e:
                print(f"Decode error: {e}")

            # Test with token
            headers = {"Authorization": f"Bearer {token}"}
            me_response = await client.get(f"{BASE_URL}/users/me", headers=headers)
            print(f"\nGET /users/me: {me_response.status_code}")
            print(f"Response: {me_response.text}")

if __name__ == "__main__":
    asyncio.run(debug())
