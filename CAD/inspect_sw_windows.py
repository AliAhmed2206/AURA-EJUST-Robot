import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32

def enum_windows_for_pid(target_pid):
    windows = []
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    
    def enum_proc(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == target_pid:
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            
            class_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_buf, 256)
            
            is_visible = user32.IsWindowVisible(hwnd)
            windows.append({
                "hwnd": hex(hwnd),
                "title": buf.value,
                "class": class_buf.value,
                "visible": is_visible
            })
        return True

    cb = WNDENUMPROC(enum_proc)
    user32.EnumWindows(cb, 0)
    return windows

import subprocess
out = subprocess.run(["powershell", "-Command", "(Get-Process -Name SLDWORKS -ErrorAction SilentlyContinue).Id"], capture_output=True, text=True).stdout.strip()
print("SLDWORKS PIDs:", out)

for pid_str in out.split():
    if pid_str.isdigit():
        pid = int(pid_str)
        wins = enum_windows_for_pid(pid)
        print(f"\nWindows for PID {pid}:")
        for w in wins:
            print(f"  HWND: {w['hwnd']}, Visible: {w['visible']}, Class: '{w['class']}', Title: '{w['title']}'")

print("Done listing windows.")
