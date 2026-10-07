"""
Creates a 1-Click Desktop Shortcut for Attendify on Windows
"""

import os
import subprocess
import winreg

def get_desktop_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders')
        desktop, _ = winreg.QueryValueEx(key, 'Desktop')
        return os.path.expandvars(desktop)
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Desktop")

desktop_dir = get_desktop_path()
shortcut_path = os.path.join(desktop_dir, "Attendify.lnk")
target_bat = os.path.abspath("launch_app.bat")
work_dir = os.path.abspath(".")
icon_path = os.path.abspath(os.path.join("assets", "logo.ico"))

vbs_script = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{target_bat}"
oLink.WorkingDirectory = "{work_dir}"
oLink.Description = "Attendify - Student Attendance Analysis"
oLink.IconLocation = "{icon_path}"
oLink.Save
"""

vbs_path = os.path.join(work_dir, "temp_shortcut.vbs")
with open(vbs_path, "w") as f:
    f.write(vbs_script)

subprocess.run(["cscript", "//nologo", vbs_path], check=True)

if os.path.exists(vbs_path):
    os.remove(vbs_path)

print(f"Desktop shortcut successfully created: {shortcut_path}")
