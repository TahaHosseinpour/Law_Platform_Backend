"""
Test script to verify project structure and basic imports
"""
import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testing imports...\n")

    tests = [
        ("app.config", "Settings"),
        ("app.database", "Database connection"),
        ("app.core.permissions", "Permissions"),
        ("app.core.security", "Security functions"),
        ("app.core.deps", "Dependencies"),
        ("app.schemas.user", "User schemas"),
        ("app.schemas.lawyer", "Lawyer schemas"),
        ("app.schemas.auth", "Auth schemas"),
        ("app.schemas.transaction", "Transaction schemas"),
        ("app.schemas.ai_chat", "AI Chat schemas"),
        ("app.schemas.blog", "Blog schemas"),
        ("app.api.auth", "Auth routes"),
        ("app.api.users", "Users routes"),
        ("app.api.lawyers", "Lawyers routes"),
        ("app.api.admin", "Admin routes"),
        ("app.api.transactions", "Transactions routes"),
        ("app.api.ai_chats", "AI Chats routes"),
        ("app.api.blog_categories", "Blog Categories routes"),
        ("app.api.blog_posts", "Blog Posts routes"),
    ]

    passed = 0
    failed = 0

    for module_name, description in tests:
        try:
            __import__(module_name)
            print(f"✅ {description:30} - OK")
            passed += 1
        except ImportError as e:
            print(f"❌ {description:30} - FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"⚠️  {description:30} - WARNING: {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"{'='*60}\n")

    return failed == 0

def test_files():
    """Test if all required files exist"""
    print("📁 Checking files...\n")

    required_files = [
        "app/main.py",
        "app/config.py",
        "app/database.py",
        "prisma/schema.prisma",
        "requirements.txt",
        ".env",
        ".env.example",
    ]

    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            missing.append(file_path)

    if missing:
        print(f"\n⚠️  Missing files: {', '.join(missing)}")
        return False

    print("\n✅ All required files exist\n")
    return True

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🧪 LAW PLATFORM - STRUCTURE TEST")
    print("="*60 + "\n")

    # Test files
    files_ok = test_files()

    # Test imports (only if not in a clean environment)
    print("\nℹ️  Import tests require dependencies to be installed.")
    print("   Run 'pip install -r requirements.txt' first.\n")

    try:
        imports_ok = test_imports()
    except Exception as e:
        print(f"⚠️  Import test skipped: {e}\n")
        imports_ok = False

    # Summary
    print("\n" + "="*60)
    if files_ok:
        print("🎉 PROJECT STRUCTURE: OK")
        if imports_ok:
            print("🎉 ALL TESTS PASSED!")
            print("\n✅ Your project is ready to run!")
            print("   Next: Run setup.ps1 to initialize")
        else:
            print("\n⚠️  Some imports failed. Make sure to:")
            print("   1. Install dependencies: pip install -r requirements.txt")
            print("   2. Generate Prisma client: prisma generate")
    else:
        print("❌ Some files are missing")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
