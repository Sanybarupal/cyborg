SANDEEP Windows Agent
=====================

This folder contains a Windows Agent scaffold for the SANDEEP assistant. It provides:
- A ToolRouter that forwards commands to a WindowsAgent
- A WindowsAgent that executes actions and performs verification
- HealthMonitor for system checks
- VoicePipeline for capture/STT/TTS
- QuickActions for left-panel actions
- A live test script to run locally on Windows

Important: This code must be run on a real Windows machine. It performs real system actions (open apps, change wallpaper, etc.).

Setup
-----
1. Create a Python 3.10+ virtualenv on your Windows machine.
2. Install requirements:

```bash
python -m pip install -r sandeep/windows_agent/requirements.txt
```

Run live tests:

```bash
python -m sandeep.windows_agent.tests.run_live_tests
```

Notes
-----
- If a required permission or executable is missing, the scripts will report errors — do not trust any "online" indicator unless verified by the checks.
- This is scaffolding to integrate into your existing assistant; you can wire the ToolRouter into your `sandeep/core/brain.py` execution pipeline.
