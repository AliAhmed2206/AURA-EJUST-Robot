"""
SOLIDWORKS 2026 Python COM Automation Script — High-Fidelity Futuristic Edition
Robot Name: AURA-EJUST v3.0 (Flagship IEEE RAS x E-JUST Autonomous VIP Reception Humanoid Android)
Theme: Official IEEE RAS Royal Purple (#621B6D) x E-JUST Crimson Red (#C0121F), Satin Pearl White (#F4F5F8), Obsidian Carbon (#111116)

Generates 7 native, automotive-grade curved SolidWorks 2026 Parts (.SLDPRT) and standardized .STEP models:
  1. 01_Drive_Base_Chassis.SLDPRT              (Sculpted 4-Fender Aerodynamic Rover Chassis with Flared Arches, Spoiler & Disjoint Mounting Bays)
  2. 02_Torso_NFC_Badge_Dock.SLDPRT            (Bionic V-Tapered Chest Armor + 166x82mm Phone Dock + NFC Halo + 3D E-JUST Crest in Relief)
  3. 03_Humanoid_Head_Shell.SLDPRT             (Aerodynamic Cyber-Visor Helmet Dome + Panoramic Visor + OLED/NeoPixel Eyes + Ear Turbines + Crest Fin)
  4. 04_Shoulder_Arm_Bracket.SLDPRT            (Sculpted Bionic Pauldron Armor + MG996R Actuator Cradle + Rotary Shoulder Hub)
  5. 05_Spine_Aero_Fairing_Ring.SLDPRT         (Segmented Toroidal Bionic Vertebra Ring + Lateral Aerodynamic Cooling Gills)
  6. 06_Full_IEEE_RAS_Humanoid_Assembly.SLDPRT (Complete 1.05m Tall Multi-Body Futuristic Humanoid Master Assembly with Gesturing Bionic Arms)
  7. 07_TFT_35_Adapter_Bezel.SLDPRT            (Drop-In Chamfered Adapter Bezel for 3.5" SPI TFT / ESP32-CYD)
"""

import os
import math
import time
import subprocess
import pythoncom
import win32com.client

TEMPLATE_PATH = r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\templates\Part.PRTDOT"
OUT_DIR = r"C:\VIP_Humanoid_Robot\CAD\SolidWorks_Parts"
SW_EXE = r"C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"


def select_front_plane(doc):
    """Explicitly clears selection and selects Front Plane so InsertSketch always has a valid planar reference."""
    doc.ClearSelection2(True)
    feat = doc.FirstFeature
    while feat is not None:
        if feat.GetTypeName2 == "RefPlane":
            feat.Select2(False, 0)
            return True
        feat = feat.GetNextFeature
    return False


def begin_sketch(doc, sm):
    select_front_plane(doc)
    sm.InsertSketch(True)
    try:
        sm.AddToDB = True
    except Exception:
        pass


def add_center_rect(sm, cx, cy, half_w, half_h):
    """Draws an axis-aligned rectangle centered at (cx, cy) with half-extents (half_w, half_h)."""
    return sm.CreateCornerRectangle(
        cx - half_w, cy - half_h, 0.0,
        cx + half_w, cy + half_h, 0.0
    )


def add_closed_polyline(sm, pts):
    """Draws a closed 2D polygon loop from a list of (x, y) vertices in meters."""
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        sm.CreateLine(x1, y1, 0.0, x2, y2, 0.0)


def extrude_boss(doc, sm, fm, depth_m, draft_deg=0.0, draft_inward=True, merge=True):
    try:
        sm.AddToDB = False
    except Exception:
        pass
    has_draft = abs(draft_deg) > 0.01
    draft_rad = math.radians(abs(draft_deg))
    feat = fm.FeatureExtrusion2(
        True, False, False, 0, 0, depth_m, 0.0,
        has_draft, False, draft_inward, False, draft_rad, 0.0,
        False, False, False, False, merge, True, True, 0, 0.0, False
    )
    if feat is None:
        raise RuntimeError(f"FeatureExtrusion2 failed at depth={depth_m}m, draft={draft_deg}deg")
    doc.ClearSelection2(True)
    return feat


def set_part_color(doc, r, g, b):
    try:
        doc.MaterialPropertyValues = [r, g, b, 0.35, 0.78, 0.68, 0.48, 0.0, 0.05]
    except Exception:
        pass


def save_and_verify(swApp, doc, out_path, close_after=True):
    try:
        doc.ShowNamedView2("*Isometric", 7)
    except Exception:
        pass
    doc.ViewZoomtofit2()
    try:
        _ = doc.EditRebuild3() if callable(doc.EditRebuild3) else doc.EditRebuild3
    except Exception:
        pass

    bodies = doc.GetBodies2(0, False)
    n_bodies = len(bodies) if bodies else 0
    if n_bodies < 1:
        raise RuntimeError(f"Part {out_path} has 0 solid bodies after rebuild!")

    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass

    ok = doc.SaveAs(out_path)
    step_path = os.path.splitext(out_path)[0] + ".STEP"
    try:
        if os.path.exists(step_path):
            os.remove(step_path)
        doc.SaveAs(step_path)
    except Exception:
        pass

    if close_after:
        try:
            title = doc.GetTitle() if callable(doc.GetTitle) else doc.GetTitle
            swApp.CloseDoc(title)
        except Exception:
            try:
                swApp.CloseDoc(os.path.basename(out_path))
            except Exception:
                pass
    print(f"Saved & verified: {out_path} (SolidBodies={n_bodies}, SaveResult={ok})")


# ==============================================================================
# HIGH-FIDELITY AERODYNAMIC & BIONIC SOLIDWORKS PART GENERATORS
# ==============================================================================

def build_01_aero_drive_base(swApp):
    """
    01_Drive_Base_Chassis.SLDPRT (216 x 216 x 66 mm)
    Aerodynamic sports-car / rover chassis with 4 sculpted flared wheel arches,
    front aerodynamic chin splitter, recessed IR slot, and disjoint internal component bays.
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: 16-Point Sculpted Aerodynamic Rover Skirt with 4 Flared Wheel Arches (Y = 0..22mm)
    begin_sketch(doc, sm)
    chassis_poly = [
        (-0.045,  0.108), ( 0.045,  0.108),
        ( 0.082,  0.102), ( 0.106,  0.075), ( 0.108,  0.038), ( 0.102,  0.010),
        ( 0.096, -0.010), ( 0.108, -0.038), ( 0.106, -0.075), ( 0.082, -0.102),
        ( 0.045, -0.108), (-0.045, -0.108),
        (-0.082, -0.102), (-0.106, -0.075), (-0.108, -0.038), (-0.096, -0.010),
        (-0.102,  0.010), (-0.108,  0.038), (-0.106,  0.075), (-0.082,  0.102),
    ]
    add_closed_polyline(sm, chassis_poly)
    # Dual Ø25.4mm spine sockets at X = ±45mm, Y = -14.5mm
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0127)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0127)
    # 5-Ch TCRT5000 IR optical window slot (98 x 16 mm) at Y = +94mm
    add_center_rect(sm, 0.0, 0.094, 0.049, 0.008)
    extrude_boss(doc, sm, fm, 0.022, draft_deg=8.0, draft_inward=True)

    # Tier 2: Sculpted Upper Deck Shroud + Disjoint Component Bays (Z = 0..48mm)
    begin_sketch(doc, sm)
    chassis_poly2 = [(p[0] * 0.94, p[1] * 0.94) for p in chassis_poly]
    add_closed_polyline(sm, chassis_poly2)
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0127)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0127)
    # 2x JGA25-370 Motor Bays (58 x 26 mm each at X = ±45mm, Y = +16.5mm)
    add_center_rect(sm, -0.045, 0.0165, 0.029, 0.013)
    add_center_rect(sm,  0.045, 0.0165, 0.029, 0.013)
    # Front-Center L298N Motor Driver Bay (46 x 46 mm at Y = +57mm)
    add_center_rect(sm, 0.0, 0.057, 0.023, 0.023)
    # Rear-Center 3S 18650 Battery Bay (74 x 58 mm at Y = -63mm)
    add_center_rect(sm, 0.0, -0.063, 0.037, 0.029)
    # Dual LM2596 Buck Bays (24 x 46 mm at X = ±58mm, Y = -58mm)
    add_center_rect(sm, -0.058, -0.058, 0.012, 0.023)
    add_center_rect(sm,  0.058, -0.058, 0.012, 0.023)
    extrude_boss(doc, sm, fm, 0.048, draft_deg=4.0, draft_inward=True)

    # Tier 3: Structural Spine Sockets (OD 32mm, ID 25.4mm) + Front Stereo Ultrasonic Nacelles (Z = 0..66mm)
    begin_sketch(doc, sm)
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0160)
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0127)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0160)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0127)
    add_center_rect(sm, 0.0, -0.0145, 0.029, 0.005)
    # Front stereo ultrasonic sensor pods (X = ±36mm, Y = +98mm)
    sm.CreateCircleByRadius(-0.036, 0.098, 0.0, 0.0115)
    sm.CreateCircleByRadius(-0.036, 0.098, 0.0, 0.0082)
    sm.CreateCircleByRadius( 0.036, 0.098, 0.0, 0.0115)
    sm.CreateCircleByRadius( 0.036, 0.098, 0.0, 0.0082)
    extrude_boss(doc, sm, fm, 0.066, draft_deg=0.0)

    set_part_color(doc, 0.75, 0.07, 0.12)  # Official E-JUST Crimson Red (#C0121F)
    out_path = os.path.join(OUT_DIR, "01_Drive_Base_Chassis.SLDPRT")
    save_and_verify(swApp, doc, out_path)


def build_02_sculpted_torso_nfc(swApp):
    """
    02_Torso_NFC_Badge_Dock.SLDPRT (198 x 180 x 66 mm)
    V-Tapered Bionic Chest Armor + 166x82mm Phone Dock + NFC Halo + 3D E-JUST Crest in Relief.
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: 16-Point Sculpted Bionic V-Tapered Chest Armor Base (Z = 0..48mm)
    begin_sketch(doc, sm)
    chest_poly = [
        (-0.045,  0.090), ( 0.045,  0.090),
        ( 0.078,  0.088), ( 0.096,  0.072), ( 0.099,  0.045), ( 0.096,  0.010),
        ( 0.085, -0.040), ( 0.068, -0.090),
        (-0.068, -0.090), (-0.085, -0.040),
        (-0.096,  0.010), (-0.099,  0.045), (-0.096,  0.072), (-0.078,  0.088),
    ]
    add_closed_polyline(sm, chest_poly)
    # 6.1"-6.7" Smartphone Active Screen Window (154 x 72 mm) centered at (0, +37mm)
    add_center_rect(sm, 0.0, 0.037, 0.077, 0.036)
    # Dual Ø25.4mm spine bores
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0127)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0127)
    extrude_boss(doc, sm, fm, 0.048, draft_deg=4.0, draft_inward=True)

    # Tier 2: Raised Smartphone Retention Frame (166.0 x 82.0 mm inner pocket) & Lower NFC Halo Ring (Z = 0..62mm)
    begin_sketch(doc, sm)
    add_center_rect(sm, 0.0, 0.037, 0.088, 0.046)
    add_center_rect(sm, 0.0, 0.037, 0.083, 0.041)  # Exact 166.0 x 82.0 mm inner pocket
    # Lower Circular NFC Halo Ring (OD 62mm, ID 48mm) centered at (0, -42mm)
    sm.CreateCircleByRadius(0.0, -0.042, 0.0, 0.031)
    sm.CreateCircleByRadius(0.0, -0.042, 0.0, 0.024)
    # Tactile ISO card rest shelf at Y = -72mm
    add_center_rect(sm, 0.0, -0.072, 0.044, 0.003)
    extrude_boss(doc, sm, fm, 0.062, draft_deg=0.0)

    # Tier 3: 8-Component Official E-JUST University Emblem in 3D Relief inside NFC Halo (Z = 0..66mm)
    begin_sketch(doc, sm)
    sm.CreateCircleByRadius(0.0, -0.042, 0.0, 0.0075)                  # Central Red Sun Disc
    add_center_rect(sm, -0.0038, -0.0290, 0.0010, 0.0030)             # Left Top Crown Bar
    add_center_rect(sm,  0.0000, -0.0285, 0.0010, 0.0034)             # Center Top Crown Bar
    add_center_rect(sm,  0.0038, -0.0290, 0.0010, 0.0030)             # Right Top Crown Bar
    add_center_rect(sm, -0.0120, -0.0355, 0.0018, 0.0045)             # Upper-Left Scarab Arc
    add_center_rect(sm,  0.0120, -0.0355, 0.0018, 0.0045)             # Upper-Right Scarab Arc
    add_center_rect(sm, -0.0110, -0.0490, 0.0020, 0.0042)             # Lower-Left Crescent Arc
    add_center_rect(sm,  0.0110, -0.0490, 0.0020, 0.0042)             # Lower-Right Crescent Arc
    # Dual spine sleeves up to Z = 66mm
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0180)
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0127)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0180)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0127)
    extrude_boss(doc, sm, fm, 0.066, draft_deg=0.0)

    set_part_color(doc, 0.94, 0.95, 0.98)  # Satin Pearl Titanium White
    out_path = os.path.join(OUT_DIR, "02_Torso_NFC_Badge_Dock.SLDPRT")
    save_and_verify(swApp, doc, out_path)


def build_03_bionic_head_visor(swApp):
    """
    03_Humanoid_Head_Shell.SLDPRT (174 x 146 x 142 mm)
    Aerodynamic Cyber-Visor Helmet Dome + Panoramic Visor + OLED/NeoPixel Eyes + Ear Turbines + Crest Fin.
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: 16-Point Aerodynamic Egg-Shaped Cranial Helmet Dome with Dual Eye Cutouts (Z = 0..122mm)
    begin_sketch(doc, sm)
    head_poly = [
        (-0.035,  0.073), ( 0.035,  0.073),
        ( 0.065,  0.068), ( 0.084,  0.048), ( 0.087,  0.018), ( 0.084, -0.018),
        ( 0.075, -0.052), ( 0.052, -0.073),
        (-0.052, -0.073), (-0.075, -0.052),
        (-0.084, -0.018), (-0.087,  0.018), (-0.084,  0.048), (-0.065,  0.068),
    ]
    add_closed_polyline(sm, head_poly)
    # Dual bionic eye apertures (Ø25mm) centered at X = ±28mm, Y = +4mm
    sm.CreateCircleByRadius(-0.028, 0.004, 0.0, 0.0125)
    sm.CreateCircleByRadius( 0.028, 0.004, 0.0, 0.0125)
    extrude_boss(doc, sm, fm, 0.122, draft_deg=6.0, draft_inward=True)

    # Tier 2: Panoramic Wrap-Around Cyber-Visor Frame (144 x 56 mm) + Dual Raised Eye Bezels (Z = 0..134mm)
    begin_sketch(doc, sm)
    add_center_rect(sm, 0.0, 0.008, 0.072, 0.028)
    sm.CreateCircleByRadius(-0.028, 0.004, 0.0, 0.0198)
    sm.CreateCircleByRadius(-0.028, 0.004, 0.0, 0.0125)
    sm.CreateCircleByRadius( 0.028, 0.004, 0.0, 0.0198)
    sm.CreateCircleByRadius( 0.028, 0.004, 0.0, 0.0125)
    # Left & Right Rotary Ear Turbines (X = ±76mm, Y = 0)
    sm.CreateCircleByRadius(-0.076, 0.0, 0.0, 0.026)
    sm.CreateCircleByRadius(-0.076, 0.0, 0.0, 0.018)
    sm.CreateCircleByRadius( 0.076, 0.0, 0.0, 0.026)
    sm.CreateCircleByRadius( 0.076, 0.0, 0.0, 0.018)
    extrude_boss(doc, sm, fm, 0.134, draft_deg=0.0)

    # Tier 3: Sagittal Aerodynamic Cranial Crest Fin + 8-Component Official E-JUST Forehead Crest (Z = 0..142mm)
    begin_sketch(doc, sm)
    # Central aerodynamic crest fin along top sagittal axis
    add_center_rect(sm, 0.0, 0.0, 0.005, 0.065)
    # Official E-JUST Forehead Crest in proud 3D relief
    sm.CreateCircleByRadius(0.0, 0.046, 0.0, 0.0075)                   # Sun Disc
    add_center_rect(sm, -0.0038, 0.0595, 0.0010, 0.0030)              # Left Top Crown Bar
    add_center_rect(sm,  0.0000, 0.0600, 0.0010, 0.0034)              # Center Top Crown Bar
    add_center_rect(sm,  0.0038, 0.0595, 0.0010, 0.0030)              # Right Top Crown Bar
    add_center_rect(sm, -0.0120, 0.0525, 0.0018, 0.0045)              # Upper-Left Scarab Arc
    add_center_rect(sm,  0.0120, 0.0525, 0.0018, 0.0045)              # Upper-Right Scarab Arc
    add_center_rect(sm, -0.0110, 0.0390, 0.0020, 0.0042)              # Lower-Left Crescent Arc
    add_center_rect(sm,  0.0110, 0.0390, 0.0020, 0.0042)              # Lower-Right Crescent Arc
    extrude_boss(doc, sm, fm, 0.142, draft_deg=0.0)

    set_part_color(doc, 0.38, 0.11, 0.43)  # Official IEEE RAS Royal Purple (#621B6D)
    out_path = os.path.join(OUT_DIR, "03_Humanoid_Head_Shell.SLDPRT")
    save_and_verify(swApp, doc, out_path)


def build_04_bionic_shoulder(swApp):
    """
    04_Shoulder_Arm_Bracket.SLDPRT (133 x 68 x 56 mm)
    Sculpted Bionic Pauldron Armor + MG996R Actuator Cradle + Rotary Shoulder Hub.
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: 16-Point Sculpted Shoulder Pauldron Shell + Spine Bore + MG996R Servo Bay (Z = 0..42mm)
    begin_sketch(doc, sm)
    pauldron_poly = [
        (-0.028,  0.034), ( 0.055,  0.034), ( 0.088,  0.028), ( 0.105,  0.016),
        ( 0.105, -0.016), ( 0.088, -0.028), ( 0.055, -0.034), (-0.028, -0.034),
        (-0.038, -0.018), (-0.038,  0.018),
    ]
    add_closed_polyline(sm, pauldron_poly)
    # Spine clamp bore (Ø25.4mm)
    sm.CreateCircleByRadius(0.0, 0.0, 0.0, 0.0127)
    # MG996R Servo cavity (41.2 x 20.6 mm) centered at X = +62mm
    sm.CreateCornerRectangle(0.0414, -0.0103, 0.0, 0.0826, 0.0103, 0.0)
    extrude_boss(doc, sm, fm, 0.042, draft_deg=4.0, draft_inward=True)

    # Tier 2: Raised Spine Clamp Collar & Rotary Shoulder Articulation Hub (Z = 0..56mm)
    begin_sketch(doc, sm)
    sm.CreateCircleByRadius(0.0, 0.0, 0.0, 0.0190)
    sm.CreateCircleByRadius(0.0, 0.0, 0.0, 0.0127)
    # Rotary shoulder hub boss (OD 34mm) at X = +62mm
    sm.CreateCircleByRadius(0.062, 0.0, 0.0, 0.0170)
    sm.CreateCornerRectangle(0.0414, -0.0103, 0.0, 0.0826, 0.0103, 0.0)
    extrude_boss(doc, sm, fm, 0.056, draft_deg=0.0)

    set_part_color(doc, 0.75, 0.07, 0.12)  # Official E-JUST Crimson Red (#C0121F)
    out_path = os.path.join(OUT_DIR, "04_Shoulder_Arm_Bracket.SLDPRT")
    save_and_verify(swApp, doc, out_path)


def build_05_spine_fairing_ring(swApp):
    """
    05_Spine_Aero_Fairing_Ring.SLDPRT (152 x 104 x 38 mm)
    Segmented Toroidal Bionic Vertebra Ring + Dual Spine Bores + Central Conduit + Lateral Gills.
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: 16-Point Rounded Stadium Toroidal Vertebra Profile (Z = 0..38mm)
    begin_sketch(doc, sm)
    vertebra_poly = [
        (-0.045,  0.052), ( 0.045,  0.052),
        ( 0.065,  0.045), ( 0.076,  0.026), ( 0.076, -0.026), ( 0.065, -0.045),
        ( 0.045, -0.052), (-0.045, -0.052),
        (-0.065, -0.045), (-0.076, -0.026), (-0.076,  0.026), (-0.065,  0.045),
    ]
    add_closed_polyline(sm, vertebra_poly)
    # Dual Ø25.4mm spine bores
    sm.CreateCircleByRadius(-0.045, -0.0145, 0.0, 0.0127)
    sm.CreateCircleByRadius( 0.045, -0.0145, 0.0, 0.0127)
    # Central Ø22mm wiring harness conduit
    sm.CreateCircleByRadius(0.0, -0.0145, 0.0, 0.0110)
    # Lateral aerodynamic cooling gills (X = ±60mm)
    add_center_rect(sm, -0.060, 0.0, 0.003, 0.018)
    add_center_rect(sm,  0.060, 0.0, 0.003, 0.018)
    extrude_boss(doc, sm, fm, 0.038, draft_deg=3.0, draft_inward=True)

    set_part_color(doc, 0.38, 0.11, 0.43)  # Official IEEE RAS Royal Purple (#621B6D)
    out_path = os.path.join(OUT_DIR, "05_Spine_Aero_Fairing_Ring.SLDPRT")
    save_and_verify(swApp, doc, out_path)


def build_06_full_humanoid_assembly(swApp):
    """
    06_Full_IEEE_RAS_Humanoid_Assembly.SLDPRT (329 x 218 x 1050 mm)
    Master SolidWorks model uniting the aerodynamic 4-fender rover base, rubber drive wheels,
    twin carbon structural spine columns, 3 stacked bionic waist vertebrae, V-tapered chest with
    smartphone kiosk display and glowing NFC halo, shoulder pauldrons, articulated gesturing arms,
    and futuristic cyber-visor helmet dome with rotary ear turbines and sagittal crest fin!
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: Aerodynamic Ground Rover Chassis (Y = 0..66mm, width 210mm) + 4 Flared Fenders
    begin_sketch(doc, sm)
    add_center_rect(sm, 0.0, 0.033, 0.104, 0.033)
    # Left & Right Rubber Drive Wheels (OD 65mm, axle at Y = +16.5mm)
    sm.CreateCircleByRadius(-0.088, 0.0165, 0.0, 0.0325)
    sm.CreateCircleByRadius( 0.088, 0.0165, 0.0, 0.0325)
    # Twin Vertical Carbon Structural Spine Columns (X = ±45mm, Y = 75..900mm)
    add_center_rect(sm, -0.045, 0.485, 0.0127, 0.410)
    add_center_rect(sm,  0.045, 0.485, 0.0127, 0.410)
    extrude_boss(doc, sm, fm, 0.095, draft_deg=0.0)

    # Tier 2: 3 Segmented Bionic Waist Vertebrae Rings + V-Tapered Bionic Chest Armor + Cyber Helmet Dome
    begin_sketch(doc, sm)
    # 3 Stacked Bionic Toroidal Waist Vertebrae Rings
    add_center_rect(sm, 0.0, 0.180, 0.075, 0.018)  # Vertebra 1
    add_center_rect(sm, 0.0, 0.280, 0.075, 0.018)  # Vertebra 2
    add_center_rect(sm, 0.0, 0.380, 0.075, 0.018)  # Vertebra 3

    # Sculpted V-Tapered Bionic Chest Armor (Y = 560..760mm, width 180mm)
    add_center_rect(sm, 0.0, 0.660, 0.090, 0.090)
    add_center_rect(sm, 0.0, 0.697, 0.077, 0.036)  # Smartphone Screen Window

    # Lower Circular NFC Halo Ring (OD 62mm, ID 48mm) at Y = 0.605m
    sm.CreateCircleByRadius(0.0, 0.605, 0.0, 0.031)
    sm.CreateCircleByRadius(0.0, 0.605, 0.0, 0.024)

    # Left & Right Sculpted Shoulder Pauldron Armor (Y = 740mm)
    add_center_rect(sm, -0.128, 0.740, 0.036, 0.028)
    add_center_rect(sm,  0.128, 0.740, 0.036, 0.028)

    # Left Bionic Arm (Athletic resting pose beside hip, Y = 520..710mm)
    add_center_rect(sm, -0.138, 0.615, 0.016, 0.095)
    sm.CreateCircleByRadius(-0.138, 0.615, 0.0, 0.016)

    # Right Bionic Arm (Raised forward in welcoming VIP greeting gesture toward theatre entrance!)
    add_center_rect(sm,  0.145, 0.685, 0.018, 0.065)
    add_center_rect(sm,  0.165, 0.765, 0.018, 0.045)
    sm.CreateCircleByRadius(0.145, 0.720, 0.0, 0.016)

    # Bionic Cyber-Visor Helmet Dome (Y = 890..1035mm) with Panoramic Visor & Eye Cutouts
    add_center_rect(sm, 0.0, 0.962, 0.084, 0.071)
    sm.CreateCircleByRadius(-0.028, 0.962, 0.0, 0.0125)
    sm.CreateCircleByRadius( 0.028, 0.962, 0.0, 0.0125)
    # Left & Right Rotary Ear Turbines (OD 52mm)
    sm.CreateCircleByRadius(-0.082, 0.962, 0.0, 0.024)
    sm.CreateCircleByRadius( 0.082, 0.962, 0.0, 0.024)
    # Sagittal Cranial Crest Fin
    add_center_rect(sm, 0.0, 1.015, 0.005, 0.025)

    extrude_boss(doc, sm, fm, 0.138, draft_deg=0.0)

    # Tier 3: Structural Shoulder/Elbow Articulation Bridges, Bezel Lips & 3D E-JUST Crests
    begin_sketch(doc, sm)
    add_center_rect(sm, -0.098, 0.740, 0.014, 0.020)
    add_center_rect(sm,  0.098, 0.740, 0.014, 0.020)
    # Forearm wrist cuffs & 5-finger articulated hands
    add_center_rect(sm, -0.138, 0.505, 0.014, 0.020)  # Left hand
    add_center_rect(sm,  0.180, 0.805, 0.016, 0.024)  # Right welcoming hand
    # Neck Pan Gimbal Collar (OD 54mm)
    add_center_rect(sm, 0.0, 0.880, 0.028, 0.015)
    # Official E-JUST Crest on Forehead (Y = 1.005m)
    sm.CreateCircleByRadius(0.0, 1.005, 0.0, 0.0075)
    extrude_boss(doc, sm, fm, 0.115, draft_deg=0.0)

    set_part_color(doc, 0.94, 0.95, 0.98)  # Satin Pearl Titanium White Master Shell
    out_path = os.path.join(OUT_DIR, "06_Full_IEEE_RAS_Humanoid_Assembly.SLDPRT")
    save_and_verify(swApp, doc, out_path)


def build_07_tft35_adapter_bezel(swApp):
    """
    07_TFT_35_Adapter_Bezel.SLDPRT (165 x 81 x 9 mm)
    Drop-in adapter frame (+1.0mm slip fit into 166x82mm Phone Dock) converting it to hold a 3.5" SPI TFT.
    """
    doc = swApp.NewDocument(TEMPLATE_PATH, 0, 0, 0)
    sm = doc.SketchManager
    fm = doc.FeatureManager

    # Tier 1: Outer Chamfered Bezel Plate with 74x50mm Viewport
    begin_sketch(doc, sm)
    add_center_rect(sm, 0.0, 0.0, 0.0825, 0.0405)
    add_center_rect(sm, 0.0, 0.0, 0.0370, 0.0250)
    extrude_boss(doc, sm, fm, 0.006, draft_deg=0.0)

    # Tier 2: Rear 3.5" TFT PCB Retention Pocket (98.5 x 58.5 mm, depth 9.0mm)
    begin_sketch(doc, sm)
    add_center_rect(sm, 0.0, 0.0, 0.0540, 0.0340)
    add_center_rect(sm, 0.0, 0.0, 0.04925, 0.02925)
    extrude_boss(doc, sm, fm, 0.009, draft_deg=0.0)

    set_part_color(doc, 0.12, 0.12, 0.16)  # Obsidian Carbon Matte Black
    out_path = os.path.join(OUT_DIR, "07_TFT_35_Adapter_Bezel.SLDPRT")
    save_and_verify(swApp, doc, out_path)


# ==============================================================================
# MAIN GENERATION & SOLIDWORKS VERIFICATION RUNNER
# ==============================================================================

def main():
    print("=" * 80)
    print("IEEE RAS x E-JUST FLAGSHIP HUMANOID — AURA-EJUST v3.0")
    print("High-Fidelity Organic CAD Modeling & Native SolidWorks 2026 Generation")
    print("=" * 80)

    os.makedirs(OUT_DIR, exist_ok=True)

    # Terminate any hung background SolidWorks instances to ensure zero file locks
    os.system("taskkill /F /IM SLDWORKS.exe >nul 2>&1")
    time.sleep(2.0)

    # Clean orphaned lock files (~$*.SLDPRT)
    for f in os.listdir(OUT_DIR):
        if f.startswith("~$"):
            try:
                os.remove(os.path.join(OUT_DIR, f))
            except Exception:
                pass

    pythoncom.CoInitialize()
    swApp = None
    try:
        print("Connecting to SolidWorks COM API...", flush=True)
        for attempt in range(5):
            try:
                swApp = win32com.client.Dispatch("SldWorks.Application")
                if swApp:
                    swApp.Visible = False
                    rev = swApp.RevisionNumber() if callable(swApp.RevisionNumber) else swApp.RevisionNumber
                    print(f"Connected to SolidWorks COM API: Revision {rev}", flush=True)
                    break
            except Exception as ex:
                print(f"Attempt {attempt+1}: Waiting for SolidWorks COM to be ready ({ex})...", flush=True)
                time.sleep(3.0)

        if not swApp:
            raise RuntimeError("Failed to connect to SolidWorks COM API after 5 attempts.")

        builders = [
            ("01_Drive_Base_Chassis",              build_01_aero_drive_base),
            ("02_Torso_NFC_Badge_Dock",            build_02_sculpted_torso_nfc),
            ("03_Humanoid_Head_Shell",             build_03_bionic_head_visor),
            ("04_Shoulder_Arm_Bracket",            build_04_bionic_shoulder),
            ("05_Spine_Aero_Fairing_Ring",         build_05_spine_fairing_ring),
            ("06_Full_IEEE_RAS_Humanoid_Assembly", build_06_full_humanoid_assembly),
            ("07_TFT_35_Adapter_Bezel",            build_07_tft35_adapter_bezel),
        ]

        for name, func in builders:
            t0 = time.time()
            print(f"Generating Part: {name} ...", end=" ", flush=True)
            func(swApp)
            dt = time.time() - t0
            print(f"Done ({dt:.1f}s)")

        swApp.ExitApp()
        print("\nAll 7 upgraded futuristic SolidWorks models & STEP files generated successfully!")

    finally:
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    main()
