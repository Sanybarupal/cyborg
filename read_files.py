#!/usr/bin/env python3
import os

os.chdir(r"c:\Users\boysa\cyborg\sandeep")

# Read files and display content
files_to_read = {
    'static/index.html': 'HTML UI',
    'static/app.js': 'JavaScript Frontend',
    'server.py': 'FastAPI Backend'
}

for filepath, desc in files_to_read.items():
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            print(f"\n{'='*60}")
            print(f"FILE: {filepath} ({desc})")
            print(f"{'='*60}")
            print(content[:2000])  # First 2000 chars
            if len(content) > 2000:
                print(f"\n... [truncated - total {len(content)} chars] ...\n")
