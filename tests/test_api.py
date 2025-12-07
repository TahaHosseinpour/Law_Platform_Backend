"""
Comprehensive API Test Script for Law Platform
Tests all endpoints with mock data
"""
import httpx
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Test results tracking
results = {"passed": 0, "failed": 0, "errors": []}


def log_result(test_name: str, success: bool, message: str = ""):
    if success:
        results["passed"] += 1
        print(f"  [PASS] {test_name}")
    else:
        results["failed"] += 1
        results["errors"].append({"test": test_name, "message": message})
        print(f"  [FAIL] {test_name}: {message}")


async def test_health_check(client: httpx.AsyncClient):
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    try:
        response = await client.get(f"{BASE_URL}/health")
        log_result("GET /health", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /health", False, str(e))


async def test_root(client: httpx.AsyncClient):
    """Test root endpoint"""
    print("\n=== Testing Root ===")
    try:
        response = await client.get(f"{BASE_URL}/")
        log_result("GET /", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /", False, str(e))


async def test_auth_endpoints(client: httpx.AsyncClient) -> dict:
    """Test authentication endpoints"""
    print("\n=== Testing Auth Endpoints ===")
    tokens = {}

    # Test user registration - Regular User
    try:
        user_data = {
            "email": f"testuser_{datetime.now().timestamp()}@test.com",
            "fullName": "Test User",
            "password": "TestPass123!",
            "role": "USER"
        }
        response = await client.post(f"{BASE_URL}/auth/register", json=user_data)
        log_result("POST /auth/register (USER)", response.status_code == 201,
                   f"Status: {response.status_code}, Response: {response.text[:200] if response.status_code != 201 else 'OK'}")

        if response.status_code == 201:
            # Test login
            login_data = {"email": user_data["email"], "password": user_data["password"]}
            login_response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            log_result("POST /auth/login (USER)", login_response.status_code == 200,
                       f"Status: {login_response.status_code}")
            if login_response.status_code == 200:
                tokens["user"] = login_response.json().get("access_token")
    except Exception as e:
        log_result("Auth USER flow", False, str(e))

    # Test user registration - Lawyer
    try:
        lawyer_data = {
            "email": f"testlawyer_{datetime.now().timestamp()}@test.com",
            "fullName": "Test Lawyer",
            "password": "LawyerPass123!",
            "role": "LAWYER"
        }
        response = await client.post(f"{BASE_URL}/auth/register", json=lawyer_data)
        log_result("POST /auth/register (LAWYER)", response.status_code == 201,
                   f"Status: {response.status_code}")

        if response.status_code == 201:
            login_data = {"email": lawyer_data["email"], "password": lawyer_data["password"]}
            login_response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            log_result("POST /auth/login (LAWYER)", login_response.status_code == 200,
                       f"Status: {login_response.status_code}")
            if login_response.status_code == 200:
                tokens["lawyer"] = login_response.json().get("access_token")
    except Exception as e:
        log_result("Auth LAWYER flow", False, str(e))

    # Test user registration - Admin
    try:
        admin_data = {
            "email": f"testadmin_{datetime.now().timestamp()}@test.com",
            "fullName": "Test Admin",
            "password": "AdminPass123!",
            "role": "ADMIN"
        }
        response = await client.post(f"{BASE_URL}/auth/register", json=admin_data)
        log_result("POST /auth/register (ADMIN)", response.status_code == 201,
                   f"Status: {response.status_code}")

        if response.status_code == 201:
            login_data = {"email": admin_data["email"], "password": admin_data["password"]}
            login_response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
            log_result("POST /auth/login (ADMIN)", login_response.status_code == 200,
                       f"Status: {login_response.status_code}")
            if login_response.status_code == 200:
                tokens["admin"] = login_response.json().get("access_token")
    except Exception as e:
        log_result("Auth ADMIN flow", False, str(e))

    # Test invalid login
    try:
        invalid_login = {"email": "invalid@test.com", "password": "wrongpass"}
        response = await client.post(f"{BASE_URL}/auth/login", json=invalid_login)
        log_result("POST /auth/login (invalid)", response.status_code == 401,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("Auth invalid login", False, str(e))

    # Debug: Print tokens
    print(f"\n  [DEBUG] Tokens received:")
    print(f"    User token: {'Yes' if tokens.get('user') else 'No'}")
    print(f"    Lawyer token: {'Yes' if tokens.get('lawyer') else 'No'}")
    print(f"    Admin token: {'Yes' if tokens.get('admin') else 'No'}")

    return tokens


async def test_user_endpoints(client: httpx.AsyncClient, tokens: dict):
    """Test user endpoints"""
    print("\n=== Testing User Endpoints ===")

    if not tokens.get("user"):
        print("  [SKIP] No user token available")
        return

    headers = {"Authorization": f"Bearer {tokens['user']}"}

    # Get current user profile
    try:
        response = await client.get(f"{BASE_URL}/users/me", headers=headers)
        log_result("GET /users/me", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /users/me", False, str(e))

    # Update current user profile
    try:
        update_data = {"fullName": "Updated Test User"}
        response = await client.put(f"{BASE_URL}/users/me", headers=headers, json=update_data)
        log_result("PUT /users/me", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("PUT /users/me", False, str(e))


async def test_lawyer_endpoints(client: httpx.AsyncClient, tokens: dict):
    """Test lawyer endpoints"""
    print("\n=== Testing Lawyer Endpoints ===")

    if not tokens.get("lawyer"):
        print("  [SKIP] No lawyer token available")
        return

    headers = {"Authorization": f"Bearer {tokens['lawyer']}"}
    lawyer_profile_id = None

    # Create lawyer profile
    try:
        profile_data = {
            "licenseNumber": f"LIC-{int(datetime.now().timestamp())}",
            "specialization": "Criminal Law",
            "experienceYears": 5,
            "bio": "Experienced criminal lawyer",
            "phoneNumber": "+989123456789",
            "address": "Tehran, Iran"
        }
        response = await client.post(f"{BASE_URL}/lawyers/profile", headers=headers, json=profile_data)
        log_result("POST /lawyers/profile", response.status_code == 201,
                   f"Status: {response.status_code}, Response: {response.text[:200] if response.status_code != 201 else 'OK'}")
        if response.status_code == 201:
            lawyer_profile_id = response.json().get("id")
    except Exception as e:
        log_result("POST /lawyers/profile", False, str(e))

    # Get my lawyer profile
    try:
        response = await client.get(f"{BASE_URL}/lawyers/profile/me", headers=headers)
        log_result("GET /lawyers/profile/me", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /lawyers/profile/me", False, str(e))

    # Update my lawyer profile
    try:
        update_data = {"bio": "Updated bio - Senior criminal lawyer"}
        response = await client.put(f"{BASE_URL}/lawyers/profile/me", headers=headers, json=update_data)
        log_result("PUT /lawyers/profile/me", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("PUT /lawyers/profile/me", False, str(e))

    # Get all lawyers (needs permission)
    if tokens.get("admin"):
        admin_headers = {"Authorization": f"Bearer {tokens['admin']}"}
        try:
            response = await client.get(f"{BASE_URL}/lawyers/", headers=admin_headers)
            log_result("GET /lawyers/", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result("GET /lawyers/", False, str(e))

        # Get lawyer by ID
        if lawyer_profile_id:
            try:
                response = await client.get(f"{BASE_URL}/lawyers/{lawyer_profile_id}", headers=admin_headers)
                log_result(f"GET /lawyers/{lawyer_profile_id}", response.status_code == 200,
                           f"Status: {response.status_code}")
            except Exception as e:
                log_result(f"GET /lawyers/{lawyer_profile_id}", False, str(e))

    return lawyer_profile_id


async def test_admin_endpoints(client: httpx.AsyncClient, tokens: dict, lawyer_profile_id: int = None):
    """Test admin endpoints"""
    print("\n=== Testing Admin Endpoints ===")

    if not tokens.get("admin"):
        print("  [SKIP] No admin token available")
        return

    headers = {"Authorization": f"Bearer {tokens['admin']}"}

    # Get all users
    try:
        response = await client.get(f"{BASE_URL}/admin/users", headers=headers)
        log_result("GET /admin/users", response.status_code == 200,
                   f"Status: {response.status_code}")
        users = response.json() if response.status_code == 200 else []
    except Exception as e:
        log_result("GET /admin/users", False, str(e))
        users = []

    # Get user by ID
    if users:
        try:
            user_id = users[0]["id"]
            response = await client.get(f"{BASE_URL}/admin/users/{user_id}", headers=headers)
            log_result(f"GET /admin/users/{user_id}", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result("GET /admin/users/{id}", False, str(e))

    # Verify lawyer
    if lawyer_profile_id:
        try:
            response = await client.patch(f"{BASE_URL}/admin/lawyers/{lawyer_profile_id}/verify", headers=headers)
            log_result(f"PATCH /admin/lawyers/{lawyer_profile_id}/verify", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result("PATCH /admin/lawyers/{id}/verify", False, str(e))

        # Unverify lawyer
        try:
            response = await client.patch(f"{BASE_URL}/admin/lawyers/{lawyer_profile_id}/unverify", headers=headers)
            log_result(f"PATCH /admin/lawyers/{lawyer_profile_id}/unverify", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result("PATCH /admin/lawyers/{id}/unverify", False, str(e))


async def test_transaction_endpoints(client: httpx.AsyncClient, tokens: dict):
    """Test transaction endpoints"""
    print("\n=== Testing Transaction Endpoints ===")

    if not tokens.get("user"):
        print("  [SKIP] No user token available")
        return

    headers = {"Authorization": f"Bearer {tokens['user']}"}
    transaction_id = None

    # Create transaction
    try:
        transaction_data = {
            "amount": "100.00",
            "type": "DEPOSIT",
            "description": "Test deposit"
        }
        response = await client.post(f"{BASE_URL}/transactions/", headers=headers, json=transaction_data)
        log_result("POST /transactions/", response.status_code == 201,
                   f"Status: {response.status_code}, Response: {response.text[:200] if response.status_code != 201 else 'OK'}")
        if response.status_code == 201:
            transaction_id = response.json().get("id")
    except Exception as e:
        log_result("POST /transactions/", False, str(e))

    # Get my transactions
    try:
        response = await client.get(f"{BASE_URL}/transactions/my-transactions", headers=headers)
        log_result("GET /transactions/my-transactions", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /transactions/my-transactions", False, str(e))

    # Get transaction by ID
    if transaction_id:
        try:
            response = await client.get(f"{BASE_URL}/transactions/{transaction_id}", headers=headers)
            log_result(f"GET /transactions/{transaction_id}", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"GET /transactions/{transaction_id}", False, str(e))

    # Admin: Complete transaction
    if tokens.get("admin") and transaction_id:
        admin_headers = {"Authorization": f"Bearer {tokens['admin']}"}
        try:
            response = await client.patch(f"{BASE_URL}/transactions/{transaction_id}/complete", headers=admin_headers)
            log_result(f"PATCH /transactions/{transaction_id}/complete", response.status_code == 200,
                       f"Status: {response.status_code}, Response: {response.text[:200] if response.status_code != 200 else 'OK'}")
        except Exception as e:
            log_result("PATCH /transactions/{id}/complete", False, str(e))

        # Get all transactions (admin)
        try:
            response = await client.get(f"{BASE_URL}/transactions/", headers=admin_headers)
            log_result("GET /transactions/ (admin)", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result("GET /transactions/ (admin)", False, str(e))


async def test_ai_chat_endpoints(client: httpx.AsyncClient, tokens: dict):
    """Test AI chat endpoints"""
    print("\n=== Testing AI Chat Endpoints ===")

    if not tokens.get("user"):
        print("  [SKIP] No user token available")
        return

    headers = {"Authorization": f"Bearer {tokens['user']}"}
    chat_id = None

    # Create chat
    try:
        chat_data = {"title": "Test Legal Question"}
        response = await client.post(f"{BASE_URL}/ai-chats/", headers=headers, json=chat_data)
        log_result("POST /ai-chats/", response.status_code == 201,
                   f"Status: {response.status_code}")
        if response.status_code == 201:
            chat_id = response.json().get("id")
    except Exception as e:
        log_result("POST /ai-chats/", False, str(e))

    # Get my chats
    try:
        response = await client.get(f"{BASE_URL}/ai-chats/", headers=headers)
        log_result("GET /ai-chats/", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /ai-chats/", False, str(e))

    if chat_id:
        # Get chat by ID
        try:
            response = await client.get(f"{BASE_URL}/ai-chats/{chat_id}", headers=headers)
            log_result(f"GET /ai-chats/{chat_id}", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"GET /ai-chats/{chat_id}", False, str(e))

        # Update chat
        try:
            update_data = {"title": "Updated Legal Question"}
            response = await client.put(f"{BASE_URL}/ai-chats/{chat_id}", headers=headers, json=update_data)
            log_result(f"PUT /ai-chats/{chat_id}", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"PUT /ai-chats/{chat_id}", False, str(e))

        # Add message to chat
        try:
            message_data = {"role": "USER", "content": "What are my legal rights?"}
            response = await client.post(f"{BASE_URL}/ai-chats/{chat_id}/messages", headers=headers, json=message_data)
            log_result(f"POST /ai-chats/{chat_id}/messages", response.status_code == 201,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"POST /ai-chats/{chat_id}/messages", False, str(e))

        # Get chat messages
        try:
            response = await client.get(f"{BASE_URL}/ai-chats/{chat_id}/messages", headers=headers)
            log_result(f"GET /ai-chats/{chat_id}/messages", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"GET /ai-chats/{chat_id}/messages", False, str(e))

        # Delete chat
        try:
            response = await client.delete(f"{BASE_URL}/ai-chats/{chat_id}", headers=headers)
            log_result(f"DELETE /ai-chats/{chat_id}", response.status_code == 204,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"DELETE /ai-chats/{chat_id}", False, str(e))


async def test_blog_category_endpoints(client: httpx.AsyncClient, tokens: dict):
    """Test blog category endpoints"""
    print("\n=== Testing Blog Category Endpoints ===")

    category_id = None

    # Create category (admin/lawyer only)
    if tokens.get("admin"):
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        try:
            category_data = {
                "name": f"Test Category {int(datetime.now().timestamp())}",
                "slug": f"test-category-{int(datetime.now().timestamp())}",
                "description": "A test category"
            }
            response = await client.post(f"{BASE_URL}/blog-categories/", headers=headers, json=category_data)
            log_result("POST /blog-categories/", response.status_code == 201,
                       f"Status: {response.status_code}")
            if response.status_code == 201:
                category_id = response.json().get("id")
        except Exception as e:
            log_result("POST /blog-categories/", False, str(e))

    # Get all categories (public)
    try:
        response = await client.get(f"{BASE_URL}/blog-categories/")
        log_result("GET /blog-categories/", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /blog-categories/", False, str(e))

    if category_id:
        # Get category by ID
        try:
            response = await client.get(f"{BASE_URL}/blog-categories/{category_id}")
            log_result(f"GET /blog-categories/{category_id}", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"GET /blog-categories/{category_id}", False, str(e))

        # Update category
        if tokens.get("admin"):
            headers = {"Authorization": f"Bearer {tokens['admin']}"}
            try:
                update_data = {"name": "Updated Category Name"}
                response = await client.put(f"{BASE_URL}/blog-categories/{category_id}", headers=headers, json=update_data)
                log_result(f"PUT /blog-categories/{category_id}", response.status_code == 200,
                           f"Status: {response.status_code}")
            except Exception as e:
                log_result(f"PUT /blog-categories/{category_id}", False, str(e))

    return category_id


async def test_blog_post_endpoints(client: httpx.AsyncClient, tokens: dict, category_id: int = None):
    """Test blog post endpoints"""
    print("\n=== Testing Blog Post Endpoints ===")

    post_id = None

    # Create post (admin/lawyer only)
    if tokens.get("admin") and category_id:
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        try:
            post_data = {
                "categoryId": category_id,
                "title": f"Test Post {int(datetime.now().timestamp())}",
                "slug": f"test-post-{int(datetime.now().timestamp())}",
                "content": "This is a test blog post content.",
                "excerpt": "Test excerpt",
                "isPublished": True
            }
            response = await client.post(f"{BASE_URL}/blog-posts/", headers=headers, json=post_data)
            log_result("POST /blog-posts/", response.status_code == 201,
                       f"Status: {response.status_code}")
            if response.status_code == 201:
                post_id = response.json().get("id")
        except Exception as e:
            log_result("POST /blog-posts/", False, str(e))

    # Get all posts (public)
    try:
        response = await client.get(f"{BASE_URL}/blog-posts/")
        log_result("GET /blog-posts/", response.status_code == 200,
                   f"Status: {response.status_code}")
    except Exception as e:
        log_result("GET /blog-posts/", False, str(e))

    if post_id:
        # Get post by ID
        try:
            response = await client.get(f"{BASE_URL}/blog-posts/{post_id}")
            log_result(f"GET /blog-posts/{post_id}", response.status_code == 200,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"GET /blog-posts/{post_id}", False, str(e))

        # Update post
        if tokens.get("admin"):
            headers = {"Authorization": f"Bearer {tokens['admin']}"}
            try:
                update_data = {"title": "Updated Post Title"}
                response = await client.put(f"{BASE_URL}/blog-posts/{post_id}", headers=headers, json=update_data)
                log_result(f"PUT /blog-posts/{post_id}", response.status_code == 200,
                           f"Status: {response.status_code}")
            except Exception as e:
                log_result(f"PUT /blog-posts/{post_id}", False, str(e))

            # Get my posts
            try:
                response = await client.get(f"{BASE_URL}/blog-posts/my-posts/", headers=headers)
                log_result("GET /blog-posts/my-posts/", response.status_code == 200,
                           f"Status: {response.status_code}")
            except Exception as e:
                log_result("GET /blog-posts/my-posts/", False, str(e))

            # Delete post
            try:
                response = await client.delete(f"{BASE_URL}/blog-posts/{post_id}", headers=headers)
                log_result(f"DELETE /blog-posts/{post_id}", response.status_code == 204,
                           f"Status: {response.status_code}")
            except Exception as e:
                log_result(f"DELETE /blog-posts/{post_id}", False, str(e))

    # Delete category (after posts deleted)
    if category_id and tokens.get("admin"):
        headers = {"Authorization": f"Bearer {tokens['admin']}"}
        try:
            response = await client.delete(f"{BASE_URL}/blog-categories/{category_id}", headers=headers)
            log_result(f"DELETE /blog-categories/{category_id}", response.status_code == 204,
                       f"Status: {response.status_code}")
        except Exception as e:
            log_result(f"DELETE /blog-categories/{category_id}", False, str(e))


async def main():
    print("=" * 60)
    print("Law Platform API Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now()}")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test basic endpoints
        await test_health_check(client)
        await test_root(client)

        # Test auth and get tokens
        tokens = await test_auth_endpoints(client)

        # Test user endpoints
        await test_user_endpoints(client, tokens)

        # Test lawyer endpoints
        lawyer_profile_id = await test_lawyer_endpoints(client, tokens)

        # Test admin endpoints
        await test_admin_endpoints(client, tokens, lawyer_profile_id)

        # Test transaction endpoints
        await test_transaction_endpoints(client, tokens)

        # Test AI chat endpoints
        await test_ai_chat_endpoints(client, tokens)

        # Test blog category endpoints
        category_id = await test_blog_category_endpoints(client, tokens)

        # Test blog post endpoints
        await test_blog_post_endpoints(client, tokens, category_id)

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Passed: {results['passed']}")
    print(f"Total Failed: {results['failed']}")
    print(f"Success Rate: {results['passed'] / (results['passed'] + results['failed']) * 100:.1f}%")

    if results["errors"]:
        print("\nFailed Tests:")
        for error in results["errors"]:
            print(f"  - {error['test']}: {error['message']}")

    print(f"\nFinished at: {datetime.now()}")


if __name__ == "__main__":
    asyncio.run(main())
