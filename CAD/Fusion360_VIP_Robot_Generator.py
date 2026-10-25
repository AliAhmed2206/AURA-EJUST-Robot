#Author: Antigravity Robotics CAD Generator — IEEE RAS x E-JUST Flagship Edition (AURA-EJUST v3.0)
#Description: Parametric 3D-Printable Component-Fit Wheeled Humanoid VIP Reception Robot Generator for Autodesk Fusion 360.
#Usage in Fusion 360: Press Shift+S (Scripts and Add-Ins) -> Click '+' next to My Scripts -> Select this folder -> Run.

import adsk.core
import adsk.fusion
import traceback
import os

def create_box(sketches, extrudes, plane, center_x, center_y, width, depth, height, operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation):
    sketch = sketches.add(plane)
    lines = sketch.sketchCurves.sketchLines
    p1 = adsk.core.Point3D.create(center_x - width / 2.0, center_y - depth / 2.0, 0)
    p2 = adsk.core.Point3D.create(center_x + width / 2.0, center_y + depth / 2.0, 0)
    lines.addTwoPointRectangle(p1, p2)
    prof = sketch.profiles.item(0)
    ext_input = extrudes.createInput(prof, operation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
    return extrudes.add(ext_input)

def create_cylinder(sketches, extrudes, plane, center_x, center_y, radius, height, operation=adsk.fusion.FeatureOperations.NewBodyFeatureOperation):
    sketch = sketches.add(plane)
    circles = sketch.sketchCurves.sketchCircles
    circles.addByCenterRadius(adsk.core.Point3D.create(center_x, center_y, 0), radius)
    prof = sketch.profiles.item(0)
    ext_input = extrudes.createInput(prof, operation)
    ext_input.setDistanceExtent(False, adsk.core.ValueInput.createByReal(height))
    return extrudes.add(ext_input)

def build_01_aero_drive_base(rootComp):
    """Part 01: 218x218x66mm Sculpted Aero Rover Base Pod with Disjoint Component Bays & Dual Spine Sockets."""
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "01_Drive_Base_Chassis"
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    xyPlane = comp.xYConstructionPlane

    # 1. Aero Base Deck + Shroud (21.8 x 21.8 cm)
    base_ext = create_cylinder(sketches, extrudes, xyPlane, 0, 0, 10.90, 2.2, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    base_ext.bodies.item(0).name = "Aero_Rover_Base_EJUST"
    create_cylinder(sketches, extrudes, xyPlane, 0, 0, 9.6, 4.4, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, 0, 0, 8.6, 3.8, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # 2. Disjoint Wheel Wells & JGA25-370 12V Geared Motor Cradles at Y = +1.65cm (X = ±7.1cm faceplates)
    create_box(sketches, extrudes, xyPlane, -9.2, 1.65, 3.2, 8.4, 2.6, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane,  9.2, 1.65, 3.2, 8.4, 2.6, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, -7.1, 1.65, 0.6, 2.9, 3.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane,  7.1, 1.65, 0.6, 2.9, 3.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # 3. Disjoint Internal Component Bays: 3S Battery (7.4x5.8cm at Y=-6.3cm), L298N (4.6x4.6cm at Y=+5.7cm), 2x LM2596 (2.4x4.6cm at X=±5.8, Y=-5.8cm), 5-Ch IR Slot (9.8x2.2cm at Y=+9.65cm)
    create_box(sketches, extrudes, xyPlane, 0, -6.3, 7.96, 6.36, 2.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0, -6.3, 7.40, 5.80, 2.4, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, -5.8, -5.8, 2.88, 5.08, 1.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane, -5.8, -5.8, 2.40, 4.60, 1.4, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane,  5.8, -5.8, 2.88, 5.08, 1.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane,  5.8, -5.8, 2.40, 4.60, 1.4, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0,  5.7, 5.12, 5.12, 1.4, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0,  5.7, 4.60, 4.60, 1.6, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0, 9.65, 9.80, 2.20, 0.8, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # 4. Disjoint Dual Gusseted Ø25.4mm Vertical Spine Sockets (X = ±4.5cm, Y = -1.45cm)
    create_cylinder(sketches, extrudes, xyPlane, -4.5, -1.45, 1.60, 6.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  4.5, -1.45, 1.60, 6.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0, -1.45, 5.8, 1.0, 4.8, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, -4.5, -1.45, 1.27, 6.8, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  4.5, -1.45, 1.27, 6.8, adsk.fusion.FeatureOperations.CutFeatureOperation)
    return comp

def build_02_sculpted_torso_nfc(rootComp):
    """Part 02: 198x180x65mm V-Tapered Bionic Chest Armor with Universal 6.1"-6.7" Smartphone Dock (166x82x11.5mm), MFRC522 NFC Halo & ESP32/DFPlayer/Speaker Stack."""
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "02_Torso_NFC_Badge_Dock"
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    xyPlane = comp.xYConstructionPlane

    ext = create_box(sketches, extrudes, xyPlane, 0, 0, 19.8, 18.0, 5.2, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.bodies.item(0).name = "Bionic_Torso_Phone_NFC_Console"
    create_box(sketches, extrudes, xyPlane, 0, 0, 18.8, 17.0, 4.6, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Upper Universal 6.1"-6.7" Smartphone Chest Kiosk Dock (16.6 x 8.2 cm pocket, 15.4 x 7.2 cm viewport)
    create_box(sketches, extrudes, xyPlane, 0, 3.7, 17.4, 8.8, 5.8, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0, 3.7, 16.6, 8.2, 5.5, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0, 3.7, 15.4, 7.2, 6.0, adsk.fusion.FeatureOperations.CutFeatureOperation)

    # Lower Circular NFC Halo Ring + MFRC522 Pocket + 8-Component Embossed Official E-JUST Emblem (Sun Disc + 3 Top Crown Bars + 4 Scarab-Lotus Arcs)
    create_cylinder(sketches, extrudes, xyPlane, 0, -3.9, 3.1, 5.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, 0, -3.9, 2.4, 5.45, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, 0, -3.85, 0.75, 5.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    for dx_bar in [-0.32, 0.0, 0.32]:
        create_box(sketches, extrudes, xyPlane, dx_bar, -2.55, 0.20, 0.56, 5.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    for sign in [-1.0, 1.0]:
        create_box(sketches, extrudes, xyPlane, sign * 1.15, -3.20, 0.36, 0.90, 5.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        create_box(sketches, extrudes, xyPlane, sign * 1.05, -4.65, 0.44, 0.90, 5.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)

    # Rear Dual Ø25.4mm Spine Clamps at X = ±4.5cm, Y = -1.45cm
    create_cylinder(sketches, extrudes, xyPlane, -4.5, -1.45, 1.82, 5.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  4.5, -1.45, 1.82, 5.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, -4.5, -1.45, 1.27, 5.4, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  4.5, -1.45, 1.27, 5.4, adsk.fusion.FeatureOperations.CutFeatureOperation)
    return comp

def build_03_bionic_head_visor(rootComp):
    """Part 03: 174x146x140mm Cyber-Visor Helmet Dome with 8-Component Official E-JUST University Forehead Emblem & Dual OLED/NeoPixel Eye Rings."""
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "03_Humanoid_Head_Shell"
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    xyPlane = comp.xYConstructionPlane

    ext = create_cylinder(sketches, extrudes, xyPlane, 0, 0, 8.7, 13.6, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.bodies.item(0).name = "Cyber_Visor_EJUST_Head"
    create_cylinder(sketches, extrudes, xyPlane, 0, 0, 7.9, 13.0, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, -2.8, 1.0, 1.6, 14.0, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  2.8, 1.0, 1.6, 14.0, adsk.fusion.FeatureOperations.CutFeatureOperation)
    # 8-Component Official E-JUST University Forehead Emblem (Central Sun Disc + 3 Top Vertical Crown Bars + 4 Scarab-Lotus Arcs)
    create_cylinder(sketches, extrudes, xyPlane, 0, 4.6, 0.85, 14.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    for dx_bar in [-0.38, 0.0, 0.38]:
        create_box(sketches, extrudes, xyPlane, dx_bar, 6.0, 0.22, 0.64, 14.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    for sign in [-1.0, 1.0]:
        create_box(sketches, extrudes, xyPlane, sign * 1.25, 5.25, 0.40, 1.00, 14.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        create_box(sketches, extrudes, xyPlane, sign * 1.15, 3.85, 0.44, 0.96, 14.2, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    return comp

def build_04_bionic_shoulder(rootComp):
    """Part 04: 133x68x56mm Open-Access Shoulder Pauldron Shroud & Precision MG996R Servo Cradle (41.2x20.6mm)."""
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "04_Shoulder_Arm_Bracket"
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    xyPlane = comp.xYConstructionPlane

    ext = create_cylinder(sketches, extrudes, xyPlane, 0, 0, 1.90, 5.6, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.bodies.item(0).name = "Shoulder_Pauldron"
    create_cylinder(sketches, extrudes, xyPlane, 5.8, 0, 3.6, 5.6, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane, 0, 0, 1.27, 5.8, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 6.2, 0, 4.12, 2.06, 5.8, adsk.fusion.FeatureOperations.CutFeatureOperation)
    return comp

def build_05_spine_fairing_ring(rootComp):
    """Part 05: 152x104x38mm Segmented Bionic Waist Exoskeleton Rib with Harness Conduit."""
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "05_Spine_Aero_Fairing_Ring"
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    xyPlane = comp.xYConstructionPlane

    ext = create_cylinder(sketches, extrudes, xyPlane, 0, 0, 7.6, 3.8, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.bodies.item(0).name = "Spine_Waist_Ring"
    create_cylinder(sketches, extrudes, xyPlane, -4.5, -1.45, 1.27, 4.0, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  4.5, -1.45, 1.27, 4.0, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_cylinder(sketches, extrudes, xyPlane,  0.0, -1.45, 1.10, 4.0, adsk.fusion.FeatureOperations.CutFeatureOperation)
    return comp

def build_07_tft35_adapter_bezel(rootComp):
    """Part 07: 165x81x9mm Optional Drop-In Adapter Frame (+1.0mm slip fit into 166x82mm Phone Dock) to 3.5-inch SPI TFT (98.5x58.5mm)."""
    occ = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = "07_TFT_35_Adapter_Bezel"
    sketches = comp.sketches
    extrudes = comp.features.extrudeFeatures
    xyPlane = comp.xYConstructionPlane

    ext = create_box(sketches, extrudes, xyPlane, 0, 0, 16.5, 8.1, 0.9, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    ext.bodies.item(0).name = "TFT35_Adapter_Bezel"
    create_box(sketches, extrudes, xyPlane, 0, 0, 9.85, 5.85, 0.6, adsk.fusion.FeatureOperations.CutFeatureOperation)
    create_box(sketches, extrudes, xyPlane, 0, 0, 7.40, 5.00, 1.1, adsk.fusion.FeatureOperations.CutFeatureOperation)
    return comp

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Please open an active Fusion 360 Design document first.')
            return

        rootComp = design.rootComponent
        comps = [
            build_01_aero_drive_base(rootComp),
            build_02_sculpted_torso_nfc(rootComp),
            build_03_bionic_head_visor(rootComp),
            build_04_bionic_shoulder(rootComp),
            build_05_spine_fairing_ring(rootComp),
            build_07_tft35_adapter_bezel(rootComp),
        ]

        out_dir = r"C:\VIP_Humanoid_Robot\STL_3D_Print_Files"
        os.makedirs(out_dir, exist_ok=True)
        exportMgr = design.exportManager
        for comp in comps:
            stlOptions = exportMgr.createSTLExportOptions(comp, os.path.join(out_dir, f"{comp.name}.stl"))
            stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            exportMgr.execute(stlOptions)

        ui.messageBox('Successfully generated all 6 AURA-EJUST v3.0 IEEE RAS x E-JUST Humanoid parts in Fusion 360!')
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
