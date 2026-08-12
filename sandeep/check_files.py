import os
import sys

# Check if server.py exists and is accessible
server_path = "server.py"
app_js_path = "static/app.js"
index_html_path = "static/index.html"

print("Checking files...")
print(f"server.py exists: {os.path.exists(server_path)}")
print(f"app.js exists: {os.path.exists(app_js_path)}")
print(f"index.html exists: {os.path.exists(index_html_path)}")

if os.path.exists(server_path):
    with open(server_path, 'r') as f:
        lines = f.readlines()
        print(f"\nserver.py has {len(lines)} lines")
        
if os.path.exists(app_js_path):
    with open(app_js_path, 'r') as f:
        content = f.read()
        print(f"\napp.js has {len(content)} chars")
        if 'voice' in content.lower():
            print("✓ Voice functionality found in app.js")
        if 'websocket' in content.lower():
            print("✓ WebSocket found in app.js")
            
if os.path.exists(index_html_path):
    with open(index_html_path, 'r') as f:
        content = f.read()
        print(f"\nindex.html has {len(content)} chars")
        if 'microphone' in content.lower() or 'voice' in content.lower():
            print("✓ Microphone/Voice UI found")
        if 'input' in content.lower():
            print("✓ Input element found")
