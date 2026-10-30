import win32com.client

print("Testing Dispatch('SldWorks.Application')...", flush=True)
try:
    swApp = win32com.client.Dispatch("SldWorks.Application")
    rev = swApp.RevisionNumber() if callable(swApp.RevisionNumber) else swApp.RevisionNumber
    print(f"Connected to SolidWorks! Revision: {rev}", flush=True)
    doc = swApp.NewDocument(r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    print("NewDocument created:", doc.GetTitle, flush=True)
    swApp.CloseDoc(doc.GetTitle)
    print("Closed document successfully!", flush=True)
except Exception as e:
    print(f"Dispatch failed: {e}", flush=True)
