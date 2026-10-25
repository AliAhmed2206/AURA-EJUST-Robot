import os
import sys
import time
import pythoncom
import win32com.client

SLDPRT_PATH = r"C:\VIP_Humanoid_Robot\CAD\SolidWorks_Parts\01_Drive_Base_Chassis.SLDPRT"
SW_EXE = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"

print(f"Target file: {SLDPRT_PATH}")
print(f"File exists: {os.path.exists(SLDPRT_PATH)}, Size: {os.path.getsize(SLDPRT_PATH)} bytes")

# Check if SLDWORKS is running
import subprocess
out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq SLDWORKS.exe"], capture_output=True, text=True).stdout
print("Current tasklist:\n", out.strip())

# Start SolidWorks using Start-Process via powershell so it runs in user GUI session
if "SLDWORKS.exe" not in out:
    print("Launching SolidWorks via PowerShell Start-Process...")
    subprocess.run(["powershell", "-Command", f'Start-Process -FilePath "{SW_EXE}"'], check=True)
    print("Waiting 15s for SolidWorks to fully initialize...")
    time.sleep(15.0)

pythoncom.CoInitialize()
swApp = None
for i in range(15):
    try:
        swApp = win32com.client.Dispatch("SldWorks.Application")
        if swApp:
            rev = swApp.RevisionNumber() if callable(swApp.RevisionNumber) else swApp.RevisionNumber
            print(f"Connected to SolidWorks COM! Revision: {rev}")
            break
    except Exception as e:
        print(f"Attempt {i+1}: {e}")
        time.sleep(2.0)

if not swApp:
    print("FAILED to connect to SolidWorks COM API!")
    sys.exit(1)

# Ensure SolidWorks is visible
swApp.Visible = True

# Try to open 01_Drive_Base_Chassis.SLDPRT
print("\nAttempting swApp.OpenDoc6...")
# Document types: swDocPART = 1
# Options: swOpenDocOptions_Silent = 1, swOpenDocOptions_ReadOnly = 2
import win32com.client
# OpenDoc6 parameters: (FileName, Type, Options, Configuration, Errors, Warnings)
errors = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
warnings = win32com.client.VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)

try:
    doc = swApp.OpenDoc6(SLDPRT_PATH, 1, 0, "", errors, warnings)
    err_val = errors.value
    warn_val = warnings.value
    print(f"OpenDoc6 returned: {doc}")
    print(f"Errors bitfield: {err_val} (hex: {hex(err_val)})")
    print(f"Warnings bitfield: {warn_val} (hex: {hex(warn_val)})")
    
    if doc:
        title = doc.GetTitle() if callable(doc.GetTitle) else doc.GetTitle
        print(f"SUCCESS! Document title: '{title}'")
        bodies = doc.GetBodies2(0, False)
        n_bodies = len(bodies) if bodies else 0
        print(f"Solid bodies in doc: {n_bodies}")
        
        # List features
        feat = doc.FirstFeature
        features = []
        while feat:
            features.append(feat.Name)
            feat = feat.GetNextFeature
        print(f"Feature tree: {features}")
    else:
        print("ERROR: OpenDoc6 returned None!")
        # Decode error
        error_flags = {
            1: "swGenericError",
            2: "swFileRequiresRepairError",
            4: "swFileWithSameTitleAlreadyOpen",
            8: "swIdMatchError",
            16: "swReadOnlyWarn",
            32: "swRequiresCodeKeyError",
            64: "swFutureVersion",
            128: "swFileTemplateWarning"
        }
        for flag, name in error_flags.items():
            if err_val & flag:
                print(f"  Flag {flag}: {name}")

except Exception as e:
    print(f"Exception during OpenDoc6: {e}")

print("\nDone diagnosing!")
