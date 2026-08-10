import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from executors.windows import WindowsExecutor

print("Starting direct executor test...")
exec = WindowsExecutor()
res = exec.open_app("notepad")
print(f"Result: {res}")
