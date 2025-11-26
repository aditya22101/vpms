"""
Script to check if backend is set up correctly
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required = [
        'flask',
        'flask_sqlalchemy',
        'flask_jwt_extended',
        'flask_cors',
        'werkzeug',
        'redis',
        'celery'
    ]
    
    missing = []
    for package in required:
        try:
            if package == 'flask_sqlalchemy':
                __import__('flask_sqlalchemy')
            elif package == 'flask_jwt_extended':
                __import__('flask_jwt_extended')
            elif package == 'flask_cors':
                __import__('flask_cors')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    return len(missing) == 0, missing

def check_database():
    """Check if database exists"""
    db_file = 'vpms.db'
    if os.path.exists(db_file):
        print(f"✅ Database file exists: {db_file}")
        return True
    else:
        print(f"⚠️  Database file not found: {db_file}")
        print("   (This is OK - it will be created on first run)")
        return True

def check_redis():
    """Check if Redis is accessible"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis is running and accessible")
        return True
    except Exception as e:
        print(f"⚠️  Redis is not accessible: {str(e)}")
        print("   (This is OK for basic functionality, but caching and Celery won't work)")
        return False

def main():
    print("=" * 50)
    print("VPMS Backend Setup Check")
    print("=" * 50)
    print()
    
    all_ok = True
    
    print("1. Checking Python version...")
    if not check_python_version():
        all_ok = False
    print()
    
    print("2. Checking dependencies...")
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        all_ok = False
        print()
        print("To install missing dependencies, run:")
        print("  pip install -r requirements.txt")
    print()
    
    print("3. Checking database...")
    check_database()
    print()
    
    print("4. Checking Redis...")
    check_redis()
    print()
    
    print("=" * 50)
    if all_ok:
        print("✅ Setup looks good! You can run the server with: python app.py")
    else:
        print("❌ Some issues found. Please fix them before running the server.")
    print("=" * 50)

if __name__ == '__main__':
    main()



