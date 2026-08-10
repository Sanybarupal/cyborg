"""
SANDEEP Screen Vision Executor — OCR and screen reading.
"""
import os
import base64
import io

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    # Default path on Windows
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class VisionExecutor:
    def execute(self, action: str, target: str = None) -> dict:
        method = getattr(self, action, None)
        if method:
            return method(target)
        return {"success": False, "message": f"Unknown vision action: {action}"}

    def ocr_screen(self, _=None) -> dict:
        if not PIL_AVAILABLE:
            return {"success": False, "message": "Pillow not installed — cannot capture screen."}

        try:
            screenshot = ImageGrab.grab()

            if TESSERACT_AVAILABLE:
                text = pytesseract.image_to_string(screenshot)
                if text.strip():
                    return {"success": True, "message": f"Screen text:\n{text[:1000]}"}
                return {"success": True, "message": "Screen captured but no readable text found."}
            else:
                # Save screenshot as base64 for potential LLM vision analysis
                buf = io.BytesIO()
                screenshot.save(buf, format="PNG")
                return {
                    "success": True,
                    "message": "Screen captured. Tesseract not installed — OCR unavailable, but screenshot taken."
                }
        except Exception as e:
            return {"success": False, "message": f"Vision error: {e}"}

    def capture_screenshot(self, _=None) -> dict:
        if not PIL_AVAILABLE:
            return {"success": False, "message": "Pillow not installed."}
        try:
            screenshot = ImageGrab.grab()
            save_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "screenshot.png")
            screenshot.save(save_path)
            return {"success": True, "message": f"Screenshot saved.", "path": save_path}
        except Exception as e:
            return {"success": False, "message": f"Screenshot failed: {e}"}
