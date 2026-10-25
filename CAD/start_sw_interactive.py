import ctypes
from ctypes import wintypes
import time

class STARTUPINFOW(ctypes.Structure):
    _fields_ = [
        ('cb', wintypes.DWORD), ('lpReserved', wintypes.LPWSTR), ('lpDesktop', wintypes.LPWSTR),
        ('lpTitle', wintypes.LPWSTR), ('dwX', wintypes.DWORD), ('dwY', wintypes.DWORD),
        ('dwXSize', wintypes.DWORD), ('dwYSize', wintypes.DWORD), ('dwXCountChars', wintypes.DWORD),
        ('dwYCountChars', wintypes.DWORD), ('dwFillAttribute', wintypes.DWORD), ('dwFlags', wintypes.DWORD),
        ('wShowWindow', wintypes.WORD), ('cbReserved2', wintypes.WORD), ('lpReserved2', ctypes.c_void_p),
        ('hStdInput', wintypes.HANDLE), ('hStdOutput', wintypes.HANDLE), ('hStdError', wintypes.HANDLE),
    ]

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [('hProcess', wintypes.HANDLE), ('hThread', wintypes.HANDLE), ('dwProcessId', wintypes.DWORD), ('dwThreadId', wintypes.DWORD)]

sw_exe = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"
sw_dir = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS"

si = STARTUPINFOW()
si.cb = ctypes.sizeof(STARTUPINFOW)
si.lpDesktop = "WinSta0\\Default"
si.dwFlags = 1
si.wShowWindow = 3 # SW_MAXIMIZE
pi = PROCESS_INFORMATION()

cmd_buf = ctypes.create_unicode_buffer(f'"{sw_exe}"')
dir_buf = ctypes.create_unicode_buffer(sw_dir)

print("Starting SolidWorks on WinSta0\\Default with working dir...", flush=True)
ok = ctypes.windll.kernel32.CreateProcessW(
    None, cmd_buf, None, None, False, 0, None, dir_buf, ctypes.byref(si), ctypes.byref(pi)
)
print("CreateProcessW ok:", ok, "PID:", pi.dwProcessId, flush=True)
ctypes.windll.kernel32.CloseHandle(pi.hThread)
ctypes.windll.kernel32.CloseHandle(pi.hProcess)
