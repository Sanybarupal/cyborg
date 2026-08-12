"""Run live tests for Windows Agent actions. Run this locally on Windows."""
from ..tool_router import ToolRouter
from ..health import HealthMonitor
from ..voice_pipeline import VoicePipeline

def run_tests():
    print("Running health checks...")
    hm = HealthMonitor()
    res = hm.check_all()
    for k, v in res.items():
        print(f"{k}: {v}")

    router = ToolRouter()
    tests = [
        {"action": "open_application", "target": "notepad"},
        {"action": "open_application", "target": "chrome"},
        {"action": "open_application", "target": "WhatsApp.exe"},
        {"action": "open_path", "target": "C:\\"},
        {"action": "system_status", "target": None},
    ]

    for t in tests:
        print("---")
        print("Test:", t)
        r = router.route(t)
        print("Result:", r)

    print("Voice quick test (requires microphone):")
    vp = VoicePipeline()
    print(vp.listen_once())


if __name__ == '__main__':
    run_tests()
