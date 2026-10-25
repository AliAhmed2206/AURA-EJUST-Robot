import os
import sys
import time

log_file = r"C:\VIP_Humanoid_Robot\CAD\debug_log.txt"

def log(msg):
    with open(log_file, "a") as f:
        f.write(f"[{time.strftime('%X')}] {msg}\n")
    print(msg, flush=True)

if os.path.exists(log_file):
    os.remove(log_file)

log("Starting debug test...")
log("Python executable: " + sys.executable)

# Check if SolidWorks is running
import win32com.client
log("Attempting GetActiveObject...")
try:
    app = win32com.client.GetActiveObject("SldWorks.Application")
    log(f"GetActiveObject succeeded! Revision: {app.RevisionNumber}")
except Exception as e:
    log(f"GetActiveObject failed: {e}")

log("Finished quick check.")
