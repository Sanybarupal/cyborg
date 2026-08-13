#!/usr/bin/env python3
"""
SANDEEP - Jarvis AI System
Quick Verification & Test Script
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def check_python():
    """Check Python version"""
    print("✓ Checking Python...")
    print(f"  Python {sys.version.split()[0]} ({sys.executable})")
    if sys.version_info < (3, 7):
        print("  ❌ Python 3.7+ required")
        return False
    print("  ✓ Python version OK")
    return True

def check_dependencies():
    """Check required packages"""
    print("\n✓ Checking dependencies...")
    
    required = [
        'fastapi',
        'uvicorn',
        'websockets',
        'pydantic',
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n  To install missing packages:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    print("\n  ✓ All dependencies OK")
    return True

def check_files():
    """Check essential files exist"""
    print("\n✓ Checking files...")
    
    files = {
        'server.py': 'FastAPI Server',
        'static/index.html': 'Frontend UI',
        'static/app.js': 'Frontend Logic',
        'static/style.css': 'Styling',
        'requirements.txt': 'Dependencies',
    }
    
    missing = []
    for filepath, desc in files.items():
        full_path = Path(filepath)
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✓ {filepath} ({size} bytes) - {desc}")
        else:
            print(f"  ❌ {filepath} - MISSING")
            missing.append(filepath)
    
    if missing:
        return False
    
    print("\n  ✓ All files present")
    return True

def check_port():
    """Check if port 8000 is available"""
    print("\n✓ Checking port 8000...")
    
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 8000))
    sock.close()
    
    if result == 0:
        print("  ⚠️  Port 8000 is in use (server might already be running)")
        return False
    else:
        print("  ✓ Port 8000 is available")
        return True

def main():
    print_header("🤖 SANDEEP - Jarvis AI System")
    print("Quick Verification & System Check\n")
    
    checks = [
        ("Python Installation", check_python),
        ("Dependencies", check_dependencies),
        ("Project Files", check_files),
        ("Port Availability", check_port),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n  ❌ Error during check: {e}")
            results[name] = False
    
    # Summary
    print_header("Summary")
    
    all_ok = all(results.values())
    
    for name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\n{'='*70}")
    
    if all_ok:
        print("\n✅ All checks passed! System is ready to run.\n")
        print("🚀 To start the server, run:")
        print("   python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload")
        print("\n   or simply run: START_SERVER.bat (Windows)")
        print("\n📖 Then visit: http://127.0.0.1:8000/")
        print("\n📝 For detailed testing guide, see: LIVE_TEST_GUIDE.md\n")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.\n")
        print("Common fixes:")
        print("  1. Install Python: https://www.python.org/")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Check that files are in correct location")
        print()
        return 1

if __name__ == '__main__':
    # Run correctly whether invoked from the project root or sandeep/ itself.
    os.chdir(Path(__file__).parent)
    sys.exit(main())
