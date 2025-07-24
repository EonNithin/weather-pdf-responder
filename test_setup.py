#!/usr/bin/env python3
"""
Test script to verify the Weather PDF Responder setup
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    """Test if environment variables are properly set"""
    print("Testing environment configuration...")
    
    load_dotenv()
    
    required_vars = ['GMAIL_ADDRESS', 'GMAIL_APP_PASSWORD', 'WEATHER_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * len(value)}")
    
    if missing_vars:
        print(f"\n❌ Missing or placeholder values for: {', '.join(missing_vars)}")
        print("Please edit your .env file with actual credentials.")
        return False
    else:
        print("\n✅ All environment variables are configured!")
        return True

def test_dependencies():
    """Test if all required packages are installed"""
    print("\nTesting dependencies...")
    
    required_packages = [
        'pandas', 'openpyxl', 'PyPDF2', 'reportlab', 
        'requests', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip3 install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies are installed!")
        return True

def test_files():
    """Test if all required files exist"""
    print("\nTesting required files...")
    
    required_files = [
        'main.py', 'requirements.txt', '.env', 
        'allowed_senders.xlsx', 'README.md'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files exist!")
        return True

def main():
    print("Weather PDF Responder - Setup Test")
    print("=" * 40)
    
    tests_passed = 0
    total_tests = 3
    
    if test_files():
        tests_passed += 1
    
    if test_dependencies():
        tests_passed += 1
        
    if test_environment():
        tests_passed += 1
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 Setup is complete! You can now run: python3 main.py")
        return 0
    else:
        print("\n⚠️  Please fix the issues above before running the main script.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
