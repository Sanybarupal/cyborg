import subprocess
import sys

# Read the existing server.py
try:
    with open(r"c:\Users\boysa\cyborg\sandeep\server.py", "r") as f:
        content = f.read()
    
    print("EXISTING SERVER.PY:")
    print("=" * 80)
    print(content[:3000])
    print("\n... [if file is longer]" if len(content) > 3000 else "")
    print(f"\nTotal length: {len(content)} characters")
    
except Exception as e:
    print(f"Error: {e}")
