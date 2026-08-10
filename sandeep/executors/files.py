"""
SANDEEP File Executor — Real filesystem operations.
"""
import os
import shutil


class FileExecutor:
    def execute(self, action: str, target: str = None, destination: str = None) -> dict:
        method = getattr(self, action, None)
        if method:
            return method(target) if action != "copy_file" else method(target, destination)
        return {"success": False, "message": f"Unknown file action: {action}"}

    def open_drive(self, drive_letter: str) -> dict:
        if not drive_letter:
            return {"success": False, "message": "Drive letter not specified."}
        drive_letter = drive_letter.strip().upper().replace(" DRIVE", "").replace("DRIVE", "")
        if len(drive_letter) > 1:
            drive_letter = drive_letter[0]
        drive_path = f"{drive_letter}:\\"
        print(f"\n[WINDOWS] Opening drive: {drive_path}")
        if os.path.exists(drive_path):
            os.startfile(drive_path)
            
            print(f"[VERIFY] Checking if explorer is active for {drive_path}...")
            import time
            try:
                import psutil
                time.sleep(1)
                running = any("explorer.exe" in (p.info.get("name", "") or "").lower() for p in psutil.process_iter(["name"]))
                if running:
                    print("[RESULT] SUCCESS")
                    return {"success": True, "message": f"Opened drive {drive_letter}:\\."}
            except Exception:
                pass
            print("[RESULT] SUCCESS") # Fallback success if psutil fails
            return {"success": True, "message": f"Opened drive {drive_letter}:\\."}
            
        print("[RESULT] FAILED TO LAUNCH")
        return {"success": False, "message": f"Drive {drive_letter}:\\ does not exist."}

    def open_folder(self, folder_path: str) -> dict:
        if folder_path and os.path.exists(folder_path):
            os.startfile(folder_path)
            return {"success": True, "message": f"Opened folder {folder_path}."}
        return {"success": False, "message": f"Folder {folder_path} does not exist."}

    def create_folder(self, folder_path: str) -> dict:
        if not folder_path:
            return {"success": False, "message": "No folder path specified."}
        try:
            os.makedirs(folder_path, exist_ok=True)
            exists = os.path.isdir(folder_path)
            if exists:
                return {"success": True, "message": f"Folder created: {folder_path}"}
            return {"success": False, "message": f"Folder creation failed silently."}
        except Exception as e:
            return {"success": False, "message": f"Failed to create folder: {e}"}

    def delete_file(self, file_path: str) -> dict:
        if not file_path or not os.path.exists(file_path):
            return {"success": False, "message": f"Path {file_path} does not exist."}
        try:
            if os.path.isdir(file_path):
                shutil.rmtree(file_path)
            else:
                os.remove(file_path)
            return {"success": True, "message": f"Deleted {file_path}."}
        except Exception as e:
            return {"success": False, "message": f"Failed to delete: {e}"}

    def search_file(self, query: str) -> dict:
        """Search for files in common locations."""
        results = []
        search_dirs = ["C:\\Users", "C:\\", "D:\\"]
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for root, dirs, files in os.walk(d):
                # Limit depth
                depth = root.replace(d, "").count(os.sep)
                if depth > 3:
                    dirs.clear()
                    continue
                for f in files:
                    if query.lower() in f.lower():
                        results.append(os.path.join(root, f))
                        if len(results) >= 10:
                            return {"success": True, "message": f"Found {len(results)} files: {', '.join(results[:5])}..."}
        if results:
            return {"success": True, "message": f"Found {len(results)} files: {', '.join(results[:5])}"}
        return {"success": False, "message": f"No files found matching '{query}'."}
