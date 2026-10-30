import time
import os
import win32com.client

print("Step 1: Terminating any leftover SLDWORKS processes...", flush=True)
os.system("taskkill /F /IM SLDWORKS.exe >nul 2>&1")
time.sleep(3.0)

print("Step 2: Connecting to SolidWorks COM API...", flush=True)
swApp = win32com.client.Dispatch("SldWorks.Application")
swApp.Visible = False
rev = swApp.RevisionNumber() if callable(swApp.RevisionNumber) else swApp.RevisionNumber
print(f"Step 3: Connected! Revision: {rev}", flush=True)

try:
    print("Step 4: Testing Part Creation...", flush=True)
    doc = swApp.NewDocument(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    title = doc.GetTitle() if callable(doc.GetTitle) else doc.GetTitle
    print(f"Step 5: Document created: {title}", flush=True)
    swApp.CloseDoc(title)
    print("Step 6: Document closed successfully.", flush=True)
finally:
    swApp.ExitApp()
    print("Step 7: SolidWorks exited cleanly.", flush=True)
