import ctypes
import time
import win32com.client
from ctypes import wintypes

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
si = STARTUPINFOW()
si.cb = ctypes.sizeof(STARTUPINFOW)
si.lpDesktop = "WinSta0\\Default"
si.dwFlags = 1
si.wShowWindow = 1
pi = PROCESS_INFORMATION()
cmd_buf = ctypes.create_unicode_buffer(f'"{sw_exe}"')

print("Launching SolidWorks on WinSta0\\Default...", flush=True)
ok = ctypes.windll.kernel32.CreateProcessW(None, cmd_buf, None, None, False, 0, None, None, ctypes.byref(si), ctypes.byref(pi))
print("CreateProcessW result:", ok, "PID:", pi.dwProcessId, flush=True)
ctypes.windll.kernel32.CloseHandle(pi.hThread)
ctypes.windll.kernel32.CloseHandle(pi.hProcess)

print("Waiting 10s for SolidWorks to register in ROT...", flush=True)
time.sleep(10.0)

swApp = None
for i in range(15):
    try:
        swApp = win32com.client.Dispatch("SldWorks.Application")
        if swApp and swApp.RevisionNumber:
            print(f"Connected to SolidWorks! Revision: {swApp.RevisionNumber}", flush=True)
            break
    except Exception as e:
        print(f"Attempt {i+1}: {e}", flush=True)
        time.sleep(2.0)

if swApp:
    print("Testing Part Creation...", flush=True)
    doc = swApp.NewDocument(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    print("Doc created:", doc.GetTitle, flush=True)
    swApp.CloseDoc(doc.GetTitle)
    print("Test passed successfully!", flush=True)
