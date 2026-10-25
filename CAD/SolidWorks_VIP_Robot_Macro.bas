Attribute VB_Name = "SolidWorks_VIP_Robot_Macro"
' =============================================================================
' SOLIDWORKS 2026 VBA MACRO: AURA-EJUST v3.0 (IEEE RAS x E-JUST FLAGSHIP EDITION)
' =============================================================================
' How to run in SolidWorks 2026:
'   1. Open SolidWorks 2026
'   2. Go to Tools -> Macro -> Run...
'   3. Select "SolidWorks_VIP_Robot_Macro.bas" and run main()
'
' Generates 7 Modular Component-Fit 3D-Printable Parts (220x220mm FDM Print Bed):
'   - 01_Drive_Base_Chassis.SLDPRT              (218 x 218 x 66 mm - Disjoint Motors Y=+16.5mm, Spine Y=-14.5mm, 3S Bat, L298N, 2x LM2596, 5-Ch IR)
'   - 02_Torso_NFC_Badge_Dock.SLDPRT            (198 x 180 x 65 mm - Universal 6.1"-6.7" Smartphone Dock 166x82mm + MFRC522 NFC Halo + E-JUST Emblem)
'   - 03_Humanoid_Head_Shell.SLDPRT             (174 x 146 x 140 mm - Official E-JUST University Forehead Emblem + Dual OLED/NeoPixel Eyes)
'   - 04_Shoulder_Arm_Bracket.SLDPRT            (133 x 68 x 56 mm  - Open-Access Pauldron + MG996R Servo Cradle 41.2x20.6mm)
'   - 05_Spine_Aero_Fairing_Ring.SLDPRT         (152 x 104 x 38 mm - Segmented Bionic Waist Rib + Dual Ø25.4mm Spine + Ø22mm Conduit)
'   - 06_Full_IEEE_RAS_Humanoid_Assembly.SLDPRT (329 x 218 x 1030 mm - Full-Scale 1.03m Humanoid Robot Multi-Body Master SolidWorks Model)
'   - 07_TFT_35_Adapter_Bezel.SLDPRT            (165 x 81 x 9 mm   - Drop-In Adapter from 166x82mm Phone Dock to 3.5" SPI TFT 98.5x58.5mm)
' =============================================================================

Option Explicit

Dim swApp As Object
Dim Part As Object

Sub SelectFrontPlane(doc As Object)
    doc.ClearSelection2 True
    Dim feat As Object
    Set feat = doc.FirstFeature
    Do While Not feat Is Nothing
        If feat.GetTypeName2 = "RefPlane" Then
            feat.Select2 False, 0
            Exit Sub
        End If
        Set feat = feat.GetNextFeature
    Loop
End Sub

Sub AddCenterRect(sm As Object, cx As Double, cy As Double, hw As Double, hh As Double)
    sm.CreateCornerRectangle cx - hw, cy - hh, 0#, cx + hw, cy + hh, 0#
End Sub

Sub main()
    Set swApp = Application.SldWorks
    Dim outFolder As String
    outFolder = "C:\VIP_Humanoid_Robot\CAD\SolidWorks_Parts\"
    
    If Dir("C:\VIP_Humanoid_Robot\CAD", vbDirectory) = "" Then MkDir "C:\VIP_Humanoid_Robot\CAD"
    If Dir(outFolder, vbDirectory) = "" Then MkDir outFolder
    
    Build01AeroDriveBase outFolder
    Build02SculptedTorsoNFC outFolder
    Build03BionicHeadVisor outFolder
    Build04BionicShoulder outFolder
    Build05SpineFairingRing outFolder
    Build06FullHumanoidAssembly outFolder
    Build07TFT35AdapterBezel outFolder
End Sub

Sub Build01AeroDriveBase(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateLine -0.078, 0.109, 0, 0.078, 0.109, 0
    Part.SketchManager.CreateLine 0.078, 0.109, 0, 0.109, 0.078, 0
    Part.SketchManager.CreateLine 0.109, 0.078, 0, 0.109, -0.078, 0
    Part.SketchManager.CreateLine 0.109, -0.078, 0, 0.078, -0.109, 0
    Part.SketchManager.CreateLine 0.078, -0.109, 0, -0.078, -0.109, 0
    Part.SketchManager.CreateLine -0.078, -0.109, 0, -0.109, -0.078, 0
    Part.SketchManager.CreateLine -0.109, -0.078, 0, -0.109, 0.078, 0
    Part.SketchManager.CreateLine -0.109, 0.078, 0, -0.078, 0.109, 0
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.0127
    AddCenterRect Part.SketchManager, 0#, 0.094, 0.049, 0.008
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.022, 0, True, False, True, False, 0.1396, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateLine -0.074, 0.104, 0, 0.074, 0.104, 0
    Part.SketchManager.CreateLine 0.074, 0.104, 0, 0.104, 0.074, 0
    Part.SketchManager.CreateLine 0.104, 0.074, 0, 0.104, -0.074, 0
    Part.SketchManager.CreateLine 0.104, -0.074, 0, 0.074, -0.104, 0
    Part.SketchManager.CreateLine 0.074, -0.104, 0, -0.074, -0.104, 0
    Part.SketchManager.CreateLine -0.074, -0.104, 0, -0.104, -0.074, 0
    Part.SketchManager.CreateLine -0.104, -0.074, 0, -0.104, 0.074, 0
    Part.SketchManager.CreateLine -0.104, 0.074, 0, -0.074, 0.104, 0
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.0127
    AddCenterRect Part.SketchManager, -0.045, 0.0165, 0.028, 0.0128
    AddCenterRect Part.SketchManager, 0.045, 0.0165, 0.028, 0.0128
    AddCenterRect Part.SketchManager, 0#, 0.057, 0.023, 0.023
    AddCenterRect Part.SketchManager, 0#, -0.063, 0.037, 0.029
    AddCenterRect Part.SketchManager, -0.058, -0.058, 0.012, 0.023
    AddCenterRect Part.SketchManager, 0.058, -0.058, 0.012, 0.023
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.048, 0, True, False, True, False, 0.0698, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.016
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.016
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCornerRectangle -0.079, 0.002, 0, -0.073, 0.031, 0
    Part.SketchManager.CreateCornerRectangle 0.073, 0.002, 0, 0.079, 0.031, 0
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.066, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "01_Drive_Base_Chassis.SLDPRT"
End Sub

Sub Build02SculptedTorsoNFC(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateLine -0.088, 0.09, 0, 0.088, 0.09, 0
    Part.SketchManager.CreateLine 0.088, 0.09, 0, 0.099, 0.076, 0
    Part.SketchManager.CreateLine 0.099, 0.076, 0, 0.099, -0.005, 0
    Part.SketchManager.CreateLine 0.099, -0.005, 0, 0.068, -0.09, 0
    Part.SketchManager.CreateLine 0.068, -0.09, 0, -0.068, -0.09, 0
    Part.SketchManager.CreateLine -0.068, -0.09, 0, -0.099, -0.005, 0
    Part.SketchManager.CreateLine -0.099, -0.005, 0, -0.099, 0.076, 0
    Part.SketchManager.CreateLine -0.099, 0.076, 0, -0.088, 0.09, 0
    AddCenterRect Part.SketchManager, 0#, 0.037, 0.077, 0.036
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.048, 0, True, False, True, False, 0.0698, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    AddCenterRect Part.SketchManager, 0#, 0.037, 0.088, 0.046
    AddCenterRect Part.SketchManager, 0#, 0.037, 0.083, 0.041
    Part.SketchManager.CreateCircleByRadius 0, -0.042, 0, 0.031
    Part.SketchManager.CreateCircleByRadius 0, -0.042, 0, 0.024
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.062, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateCircleByRadius 0, -0.042, 0, 0.0065
    AddCenterRect Part.SketchManager, -0.0035, -0.0295, 0.0009, 0.0028
    AddCenterRect Part.SketchManager, 0#, -0.029, 0.0009, 0.0032
    AddCenterRect Part.SketchManager, 0.0035, -0.0295, 0.0009, 0.0028
    AddCenterRect Part.SketchManager, -0.0115, -0.0355, 0.0018, 0.0042
    AddCenterRect Part.SketchManager, 0.0115, -0.0355, 0.0018, 0.0042
    AddCenterRect Part.SketchManager, -0.0105, -0.0485, 0.002, 0.0042
    AddCenterRect Part.SketchManager, 0.0105, -0.0485, 0.002, 0.0042
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.065, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "02_Torso_NFC_Badge_Dock.SLDPRT"
End Sub

Sub Build03BionicHeadVisor(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateLine -0.058, 0.073, 0, 0.058, 0.073, 0
    Part.SketchManager.CreateLine 0.058, 0.073, 0, 0.087, 0.044, 0
    Part.SketchManager.CreateLine 0.087, 0.044, 0, 0.087, -0.044, 0
    Part.SketchManager.CreateLine 0.087, -0.044, 0, 0.058, -0.073, 0
    Part.SketchManager.CreateLine 0.058, -0.073, 0, -0.058, -0.073, 0
    Part.SketchManager.CreateLine -0.058, -0.073, 0, -0.087, -0.044, 0
    Part.SketchManager.CreateLine -0.087, -0.044, 0, -0.087, 0.044, 0
    Part.SketchManager.CreateLine -0.087, 0.044, 0, -0.058, 0.073, 0
    Part.SketchManager.CreateCircleByRadius -0.028, 0.004, 0, 0.0125
    Part.SketchManager.CreateCircleByRadius 0.028, 0.004, 0, 0.0125
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.122, 0, True, False, True, False, 0.1047, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateCircleByRadius -0.028, 0.004, 0, 0.0198
    Part.SketchManager.CreateCircleByRadius -0.028, 0.004, 0, 0.0125
    Part.SketchManager.CreateCircleByRadius 0.028, 0.004, 0, 0.0198
    Part.SketchManager.CreateCircleByRadius 0.028, 0.004, 0, 0.0125
    Part.SketchManager.CreateCircleByRadius 0, 0.044, 0, 0.0075
    AddCenterRect Part.SketchManager, -0.0038, 0.0575, 0.001, 0.003
    AddCenterRect Part.SketchManager, 0#, 0.058, 0.001, 0.0034
    AddCenterRect Part.SketchManager, 0.0038, 0.0575, 0.001, 0.003
    AddCenterRect Part.SketchManager, -0.012, 0.0505, 0.0018, 0.0045
    AddCenterRect Part.SketchManager, 0.012, 0.0505, 0.0018, 0.0045
    AddCenterRect Part.SketchManager, -0.011, 0.037, 0.002, 0.0042
    AddCenterRect Part.SketchManager, 0.011, 0.037, 0.002, 0.0042
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.14, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "03_Humanoid_Head_Shell.SLDPRT"
End Sub

Sub Build04BionicShoulder(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateLine -0.028, 0.034, 0, 0.085, 0.034, 0
    Part.SketchManager.CreateLine 0.085, 0.034, 0, 0.105, 0.018, 0
    Part.SketchManager.CreateLine 0.105, 0.018, 0, 0.105, -0.018, 0
    Part.SketchManager.CreateLine 0.105, -0.018, 0, 0.085, -0.034, 0
    Part.SketchManager.CreateLine 0.085, -0.034, 0, -0.028, -0.034, 0
    Part.SketchManager.CreateLine -0.028, -0.034, 0, -0.038, -0.018, 0
    Part.SketchManager.CreateLine -0.038, -0.018, 0, -0.038, 0.018, 0
    Part.SketchManager.CreateLine -0.038, 0.018, 0, -0.028, 0.034, 0
    Part.SketchManager.CreateCircleByRadius 0, 0, 0, 0.0127
    Part.SketchManager.CreateCornerRectangle 0.0414, -0.0103, 0, 0.0826, 0.0103, 0
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.042, 0, True, False, True, False, 0.0698, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateCircleByRadius 0, 0, 0, 0.0185
    Part.SketchManager.CreateCircleByRadius 0, 0, 0, 0.0127
    AddCenterRect Part.SketchManager, 0.062, 0#, 0.026, 0.015
    Part.SketchManager.CreateCornerRectangle 0.0414, -0.0103, 0, 0.0826, 0.0103, 0
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.056, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "04_Shoulder_Arm_Bracket.SLDPRT"
End Sub

Sub Build05SpineFairingRing(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateLine -0.052, 0.052, 0, 0.052, 0.052, 0
    Part.SketchManager.CreateLine 0.052, 0.052, 0, 0.076, 0.028, 0
    Part.SketchManager.CreateLine 0.076, 0.028, 0, 0.076, -0.028, 0
    Part.SketchManager.CreateLine 0.076, -0.028, 0, 0.052, -0.052, 0
    Part.SketchManager.CreateLine 0.052, -0.052, 0, -0.052, -0.052, 0
    Part.SketchManager.CreateLine -0.052, -0.052, 0, -0.076, -0.028, 0
    Part.SketchManager.CreateLine -0.076, -0.028, 0, -0.076, 0.028, 0
    Part.SketchManager.CreateLine -0.076, 0.028, 0, -0.052, 0.052, 0
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCircleByRadius 0, -0.0145, 0, 0.011
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.028, 0, True, False, True, False, 0.0698, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.0175
    Part.SketchManager.CreateCircleByRadius -0.045, -0.0145, 0, 0.0127
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.0175
    Part.SketchManager.CreateCircleByRadius 0.045, -0.0145, 0, 0.0127
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.038, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "05_Spine_Aero_Fairing_Ring.SLDPRT"
End Sub

Sub Build06FullHumanoidAssembly(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    AddCenterRect Part.SketchManager, 0#, 0.033, 0.109, 0.033
    AddCenterRect Part.SketchManager, -0.045, 0.485, 0.0127, 0.41
    AddCenterRect Part.SketchManager, 0.045, 0.485, 0.0127, 0.41
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.11, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    AddCenterRect Part.SketchManager, 0#, 0.068, 0.065, 0.018
    AddCenterRect Part.SketchManager, 0#, 0.25, 0.076, 0.019
    AddCenterRect Part.SketchManager, 0#, 0.43, 0.076, 0.019
    AddCenterRect Part.SketchManager, 0#, 0.67, 0.099, 0.09
    AddCenterRect Part.SketchManager, 0#, 0.707, 0.077, 0.036
    AddCenterRect Part.SketchManager, -0.135, 0.725, 0.028, 0.03
    AddCenterRect Part.SketchManager, 0.135, 0.725, 0.028, 0.03
    AddCenterRect Part.SketchManager, -0.138, 0.555, 0.018, 0.125
    AddCenterRect Part.SketchManager, 0.138, 0.555, 0.018, 0.125
    AddCenterRect Part.SketchManager, 0#, 0.96, 0.087, 0.068
    Part.SketchManager.CreateCircleByRadius -0.028, 0.96, 0, 0.0125
    Part.SketchManager.CreateCircleByRadius 0.028, 0.96, 0, 0.0125
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.14, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    AddCenterRect Part.SketchManager, -0.103, 0.725, 0.012, 0.022
    AddCenterRect Part.SketchManager, 0.103, 0.725, 0.012, 0.022
    AddCenterRect Part.SketchManager, -0.138, 0.688, 0.016, 0.015
    AddCenterRect Part.SketchManager, 0.138, 0.688, 0.016, 0.015
    AddCenterRect Part.SketchManager, 0#, 0.885, 0.058, 0.018
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.105, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "06_Full_IEEE_RAS_Humanoid_Assembly.SLDPRT"
End Sub

Sub Build07TFT35AdapterBezel(outFolder As String)
    Set Part = swApp.NewDocument("C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT", 0, 0, 0)
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    AddCenterRect Part.SketchManager, 0#, 0#, 0.0825, 0.0405
    AddCenterRect Part.SketchManager, 0#, 0#, 0.037, 0.025
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.006, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    SelectFrontPlane Part
    Part.SketchManager.InsertSketch True
    Part.SketchManager.AddToDB = True
    AddCenterRect Part.SketchManager, 0#, 0#, 0.054, 0.034
    AddCenterRect Part.SketchManager, 0#, 0#, 0.04925, 0.02925
    Part.SketchManager.AddToDB = False
    Part.FeatureManager.FeatureExtrusion2 True, False, False, 0, 0, 0.009, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False
    
    Part.ViewZoomtofit2
    Part.SaveAs outFolder & "07_TFT_35_Adapter_Bezel.SLDPRT"
End Sub
