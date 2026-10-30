import os
import sys
import time
import threading

log_file = r"C:\VIP_Humanoid_Robot\CAD\debug_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(f"[{time.strftime('%X')}] {msg}\n")
    print(msg, flush=True)

log("Starting Dispatch test in thread...")

def dispatch_worker():
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    try:
        log("Calling Dispatch('SldWorks.Application')...")
        swApp = win32com.client.Dispatch("SldWorks.Application")
        log(f"Dispatch returned! Revision: {swApp.RevisionNumber}")
    except Exception as e:
        log(f"Dispatch raised exception: {e}")
    finally:
        pythoncom.CoUninitialize()

t = threading.Thread(target=dispatch_worker, daemon=True)
t.start()
t.join(timeout=10.0)

if t.is_alive():
    log("Dispatch is HUNG after 10 seconds! SLDWORKS is stuck initializing via DCOM.")
else:
    log("Dispatch completed within 10 seconds.")
