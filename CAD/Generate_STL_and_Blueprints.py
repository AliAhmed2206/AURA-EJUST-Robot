"""
IEEE RAS x E-JUST Flagship Edition — Parametric Lofted 3D-Printable STL & High-Fidelity CAD Renderer
Robot Name: AURA-EJUST v3.0 (Autonomous VIP Reception & Escort Humanoid Android)
Theme: Official IEEE RAS (Royal Purple #621B6D & Crimson #860038) x E-JUST (Crimson Red #C0121F, Obsidian Carbon #111116, Pearl White #F4F5F8, Glowing Magenta #FF1493)

Industrial Design: Automotive Concept Supercar Rover Platform with 4 Flared Wheel Arches,
Chunky Black Rubber Wheels with Glowing Magenta Rim Halos, Segmented Bionic Toroidal Spine (4 Stacked Vertebrae Rings),
Athletic V-Tapered Chest with Shield-Shaped Kiosk Display & Glowing Circular NFC Tap Halo,
Articulated Bionic Arms with 5-Finger Robotic Hands (Welcoming Right Hand Gesture),
and Sleek Aerodynamic Cyber-Visor Android Helmet Dome with Dual Glowing Circular Eye Rings.

All individual parts fit standard 220x220mm FDM build plates and have mathematically verified
pairwise-disjoint internal component pockets:
  - 01_Drive_Base_Chassis.stl         (216 x 216 x 66 mm) -> Disjoint bays for 2x JGA25-370 motors (Y=+16.5mm), dual Ø25.4mm spine sockets (X=±45, Y=-14.5mm), 3S 18650/12V battery (Y=-63mm), L298N (Y=+57mm), 2x LM2596 bucks (X=±58, Y=-58mm), 5-Ch TCRT5000 IR bar + floor optical slot (Y=+96.5mm), 3x ball casters, 2x HC-SR04 ultrasonics, rear switch/jack.
  - 02_Torso_NFC_Badge_Dock.stl       (196 x 106 x 180 mm) -> 10° tilted Universal 6.1"-6.7" Smartphone Chest Kiosk Dock (166.0x82.0x11.5mm pocket + top slide-in loading slot + 154x72mm viewport + USB-C channel), lower NFC Halo + 42x62mm MFRC522 pocket (1.5mm RF wall), and non-overlapping central spine bridge stack: ESP32 DevKit V1 (31x58mm at Z=136), DFPlayer Mini (23x23mm at Z=82), and Ø40mm speaker chamber (Z=36).
  - 03_Humanoid_Head_Shell.stl        (172 x 136 x 142 mm) -> Official E-JUST University Forehead Crest (Sun Disc + 3 Crown Bars + Scarab-Lotus Arcs), panoramic wrap-around cyber-visor, dual 0.96"/1.3" OLED + 12-Bit WS2812B NeoPixel eye mounts, rotary ear turbines, sagittal cranial crest fin, MG996R neck pan gimbal collar.
  - 04_Shoulder_Arm_Bracket.stl       (132 x 68 x 56 mm)  -> Open-access contoured spherical pauldron armor with precision MG996R/DS3218 servo cradle (41.2x20.6x42.0mm + M4 mounting tabs) + Ø25.4mm spine clamp.
  - 05_Spine_Aero_Fairing_Ring.stl    (148 x 100 x 36 mm) -> Segmented bionic toroidal vertebra ring with dual Ø25.4mm spine bores + central Ø22mm wiring harness conduit + lateral cooling vent gills.
  - 06_Full_IEEE_RAS_Humanoid_Assembly.stl (360 x 320 x 840 mm) -> Full multi-material reference assembly matching IEEE_RAS_EJUST_Humanoid_Showcase.jpg.
  - 07_TFT_35_Adapter_Bezel.stl       (165 x 81 x 9 mm)   -> Drop-in adapter frame (+1.0mm slip fit into the 166x82mm smartphone chest pocket) converting it to hold a 3.5" ILI9488 SPI TFT / ESP32-CYD display (98.5x58.5mm).
"""

import os
import struct
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ==============================================================================
# AUTHORITATIVE COMPONENT BAY LAYOUT & CLEARANCE SPECIFICATION
# ==============================================================================

BASE_CHASSIS_BAYS_2D = {
    # name: (cx, cy, outer_wx, outer_wy, inner_wx, inner_wy, inner_wz)
    "Left_Spine_Socket":   (-45.0, -14.5, 32.0, 32.0, 25.4, 25.4, 66.0),
    "Right_Spine_Socket":  ( 45.0, -14.5, 32.0, 32.0, 25.4, 25.4, 66.0),
    "Left_JGA25_Motor":    (-45.0,  16.5, 58.0, 29.0, 62.0, 25.6, 36.0),
    "Right_JGA25_Motor":   ( 45.0,  16.5, 58.0, 29.0, 62.0, 25.6, 36.0),
    "Battery_3S_18650":    (  0.0, -63.0, 79.6, 63.6, 74.0, 58.0, 22.0),
    "Buck_LM2596_5V":      (-58.0, -58.0, 28.8, 50.8, 24.0, 46.0, 20.0),
    "Buck_LM2596_6V":      ( 58.0, -58.0, 28.8, 50.8, 24.0, 46.0, 20.0),
    "L298N_Driver":        (  0.0,  57.0, 51.2, 51.2, 46.0, 46.0, 32.0),
    "Front_Caster_Left":   (-44.0,  57.0, 26.0, 26.0, 24.0, 24.0, 12.0),
    "Front_Caster_Right":  ( 44.0,  57.0, 26.0, 26.0, 24.0, 24.0, 12.0),
    "Rear_Caster_Left":    (-52.0, -94.5, 20.0, 20.0, 18.0, 18.0, 12.0),
    "Rear_Caster_Right":   ( 52.0, -94.5, 20.0, 20.0, 18.0, 18.0, 12.0),
    "IR_5Ch_TCRT5000":     (  0.0,  96.5,103.0, 26.8, 98.0, 22.0, 10.0),
}

TORSO_BRIDGE_BAYS_XZ = {
    # name: (cx, cz, outer_wx, outer_wz, inner_wx, inner_wz, inner_depth)
    "Left_Torso_Spine":    (-45.0,  88.0, 36.4, 176.0, 25.4, 176.0, 25.4),
    "Right_Torso_Spine":   ( 45.0,  88.0, 36.4, 176.0, 25.4, 176.0, 25.4),
    "ESP32_DevKit_V1":     (  0.0, 136.0, 35.8,  62.8, 31.0,  58.0, 12.0),
    "DFPlayer_Mini":       (  0.0,  82.0, 27.4,  27.4, 23.0,  23.0, 10.0),
    "Speaker_40mm":        (  0.0,  36.0, 46.0,  46.0, 41.0,  41.0, 16.0),
}

SMARTPHONE_DOCK_SPEC = {
    "inner_width_mm":   166.0,
    "inner_height_mm":   82.0,
    "inner_depth_mm":    11.5,
    "viewport_w_mm":    154.0,
    "viewport_h_mm":     72.0,
    "adapter_outer_w":  165.0,
    "adapter_outer_h":   81.0,
    "adapter_outer_d":    9.0,
}

# ==============================================================================
# GEOMETRIC PRIMITIVES & VECTORIZED SURFACE ENGINES
# ==============================================================================

def superellipse_point(theta, rx, ry, n=2.5):
    ct = math.cos(theta)
    st = math.sin(theta)
    x = rx * (abs(ct) ** (2.0 / n)) * (1.0 if ct >= 0 else -1.0)
    y = ry * (abs(st) ** (2.0 / n)) * (1.0 if st >= 0 else -1.0)
    return x, y

def create_lofted_shell(z_slices, wall_thickness=4.0, segments=52, cap_bottom=True, cap_top=False):
    tris = []
    angles = np.linspace(0, 2 * np.pi, segments + 1)
    num_s = len(z_slices)

    outer_rings = []
    inner_rings = []
    for (z, cx, cy, rx, ry, n_exp) in z_slices:
        o_ring = []
        i_ring = []
        irx = max(2.0, rx - wall_thickness)
        iry = max(2.0, ry - wall_thickness)
        for a in angles[:-1]:
            ox, oy = superellipse_point(a, rx, ry, n_exp)
            ix, iy = superellipse_point(a, irx, iry, n_exp)
            o_ring.append([cx + ox, cy + oy, z])
            i_ring.append([cx + ix, cy + iy, z])
        outer_rings.append(o_ring)
        inner_rings.append(i_ring)

    for s in range(num_s - 1):
        r0 = outer_rings[s]
        r1 = outer_rings[s + 1]
        for i in range(segments):
            inext = (i + 1) % segments
            p00, p01 = r0[i], r0[inext]
            p10, p11 = r1[i], r1[inext]
            tris.append([p00, p01, p11])
            tris.append([p00, p11, p10])

    if wall_thickness > 0:
        for s in range(num_s - 1):
            r0 = inner_rings[s]
            r1 = inner_rings[s + 1]
            for i in range(segments):
                inext = (i + 1) % segments
                p00, p01 = r0[i], r0[inext]
                p10, p11 = r1[i], r1[inext]
                tris.append([p00, p11, p01])
                tris.append([p00, p10, p11])

        if not cap_top:
            rt_o = outer_rings[-1]
            rt_i = inner_rings[-1]
            for i in range(segments):
                inext = (i + 1) % segments
                tris.append([rt_i[i], rt_o[i], rt_o[inext]])
                tris.append([rt_i[i], rt_o[inext], rt_i[inext]])
        else:
            z_top, cx_t, cy_t, _, _, _ = z_slices[-1]
            ct = [cx_t, cy_t, z_top]
            rt_o = outer_rings[-1]
            for i in range(segments):
                inext = (i + 1) % segments
                tris.append([ct, rt_o[i], rt_o[inext]])

        if cap_bottom:
            z_bot, cx_b, cy_b, _, _, _ = z_slices[0]
            cb = [cx_b, cy_b, z_bot]
            rb_o = outer_rings[0]
            for i in range(segments):
                inext = (i + 1) % segments
                tris.append([cb, rb_o[inext], rb_o[i]])
        else:
            rb_o = outer_rings[0]
            rb_i = inner_rings[0]
            for i in range(segments):
                inext = (i + 1) % segments
                tris.append([rb_i[i], rb_o[inext], rb_o[i]])
                tris.append([rb_i[i], rb_i[inext], rb_o[inext]])
    else:
        if cap_bottom:
            z_bot, cx_b, cy_b, _, _, _ = z_slices[0]
            cb = [cx_b, cy_b, z_bot]
            rb_o = outer_rings[0]
            for i in range(segments):
                inext = (i + 1) % segments
                tris.append([cb, rb_o[inext], rb_o[i]])
        if cap_top:
            z_top, cx_t, cy_t, _, _, _ = z_slices[-1]
            ct = [cx_t, cy_t, z_top]
            rt_o = outer_rings[-1]
            for i in range(segments):
                inext = (i + 1) % segments
                tris.append([ct, rt_o[i], rt_o[inext]])

    return np.array(tris, dtype=np.float32)

def create_box_triangles(cx, cy, cz, wx, wy, wz):
    x0, x1 = cx - wx / 2.0, cx + wx / 2.0
    y0, y1 = cy - wy / 2.0, cy + wy / 2.0
    z0, z1 = cz - wz / 2.0, cz + wz / 2.0
    v = np.array([
        [x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
        [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]
    ], dtype=np.float32)
    faces = [
        (0, 2, 1), (0, 3, 2),
        (4, 5, 6), (4, 6, 7),
        (0, 1, 5), (0, 5, 4),
        (2, 3, 7), (2, 7, 6),
        (0, 4, 7), (0, 7, 3),
        (1, 2, 6), (1, 6, 5)
    ]
    return np.array([[v[i], v[j], v[k]] for (i, j, k) in faces], dtype=np.float32)

def create_walled_pocket(cx, cy, cz_bottom, inner_wx, inner_wy, wall_h, wall_t=2.6, standoffs=None):
    parts = []
    zc = cz_bottom + wall_h / 2.0
    total_wx = inner_wx + 2.0 * wall_t
    parts.append(create_box_triangles(cx, cy + (inner_wy + wall_t) / 2.0, zc, total_wx, wall_t, wall_h))
    parts.append(create_box_triangles(cx, cy - (inner_wy + wall_t) / 2.0, zc, total_wx, wall_t, wall_h))
    parts.append(create_box_triangles(cx - (inner_wx + wall_t) / 2.0, cy, zc, wall_t, inner_wy, wall_h))
    parts.append(create_box_triangles(cx + (inner_wx + wall_t) / 2.0, cy, zc, wall_t, inner_wy, wall_h))
    if standoffs:
        for (dx, dy, bh) in standoffs:
            parts.append(create_cylinder_along_axis(cx + dx, cy + dy, cz_bottom + bh / 2.0, 1.5, 3.6, bh, 18, axis='z'))
    return np.concatenate(parts, axis=0)

def create_cylinder_along_axis(cx, cy, cz, r_inner, r_outer, length, segments=36, axis='z'):
    tris = []
    angles = np.linspace(0, 2 * np.pi, segments + 1)
    h0, h1 = -length / 2.0, length / 2.0

    def to_xyz(u, v, w):
        if axis == 'z':
            return [cx + u, cy + v, cz + w]
        elif axis == 'y':
            return [cx + u, cy + w, cz + v]
        else:
            return [cx + w, cy + u, cz + v]

    for i in range(segments):
        a0, a1 = angles[i], angles[i + 1]
        c0, s0 = math.cos(a0), math.sin(a0)
        c1, s1 = math.cos(a1), math.sin(a1)
        if r_inner <= 0.001:
            pb0 = to_xyz(r_outer * c0, r_outer * s0, h0)
            pb1 = to_xyz(r_outer * c1, r_outer * s1, h0)
            pt0 = to_xyz(r_outer * c0, r_outer * s0, h1)
            pt1 = to_xyz(r_outer * c1, r_outer * s1, h1)
            cb = to_xyz(0.0, 0.0, h0)
            ct = to_xyz(0.0, 0.0, h1)
            tris.append([cb, pb1, pb0])
            tris.append([ct, pt0, pt1])
            tris.append([pb0, pb1, pt1])
            tris.append([pb0, pt1, pt0])
        else:
            ob0 = to_xyz(r_outer * c0, r_outer * s0, h0)
            ob1 = to_xyz(r_outer * c1, r_outer * s1, h0)
            ot0 = to_xyz(r_outer * c0, r_outer * s0, h1)
            ot1 = to_xyz(r_outer * c1, r_outer * s1, h1)
            ib0 = to_xyz(r_inner * c0, r_inner * s0, h0)
            ib1 = to_xyz(r_inner * c1, r_inner * s1, h0)
            it0 = to_xyz(r_inner * c0, r_inner * s0, h1)
            it1 = to_xyz(r_inner * c1, r_inner * s1, h1)
            tris.append([ob0, ob1, ot1])
            tris.append([ob0, ot1, ot0])
            tris.append([ib0, it1, ib1])
            tris.append([ib0, it0, it1])
            tris.append([it0, ot0, ot1])
            tris.append([it0, ot1, it1])
            tris.append([ib0, ob1, ob0])
            tris.append([ib0, ib1, ob1])

    return np.array(tris, dtype=np.float32)

def create_torus(cx, cy, cz, r_major, r_minor, segments_u=40, segments_v=24, scale_x=1.0, scale_y=1.0):
    u = np.linspace(0, 2*np.pi, segments_u, endpoint=False)
    v = np.linspace(0, 2*np.pi, segments_v, endpoint=False)
    U, V = np.meshgrid(u, v)
    X = (r_major + r_minor * np.cos(V)) * np.cos(U) * scale_x + cx
    Y = (r_major + r_minor * np.cos(V)) * np.sin(U) * scale_y + cy
    Z = r_minor * np.sin(V) + cz
    tris = []
    for i in range(segments_v):
        inext = (i + 1) % segments_v
        for j in range(segments_u):
            jnext = (j + 1) % segments_u
            p00 = [X[i, j], Y[i, j], Z[i, j]]
            p01 = [X[i, jnext], Y[i, jnext], Z[i, jnext]]
            p10 = [X[inext, j], Y[inext, j], Z[inext, j]]
            p11 = [X[inext, jnext], Y[inext, jnext], Z[inext, jnext]]
            tris.append([p00, p01, p11])
            tris.append([p00, p11, p10])
    return np.array(tris, dtype=np.float32)

def create_ellipsoid(cx, cy, cz, rx, ry, rz, segments_lat=20, segments_lon=32):
    theta = np.linspace(0, np.pi, segments_lat)
    phi = np.linspace(0, 2*np.pi, segments_lon, endpoint=False)
    T, P = np.meshgrid(theta, phi)
    X = rx * np.sin(T) * np.cos(P) + cx
    Y = ry * np.sin(T) * np.sin(P) + cy
    Z = rz * np.cos(T) + cz
    tris = []
    for i in range(segments_lon):
        inext = (i + 1) % segments_lon
        for j in range(segments_lat - 1):
            jnext = j + 1
            p00 = [X[i, j], Y[i, j], Z[i, j]]
            p01 = [X[i, jnext], Y[i, jnext], Z[i, jnext]]
            p10 = [X[inext, j], Y[inext, j], Z[inext, j]]
            p11 = [X[inext, jnext], Y[inext, jnext], Z[inext, jnext]]
            tris.append([p00, p01, p11])
            tris.append([p00, p11, p10])
    return np.array(tris, dtype=np.float32)

def transform_triangles(tris, scale=1.0, rx_deg=0.0, ry_deg=0.0, rz_deg=0.0, tx=0.0, ty=0.0, tz=0.0):
    pts = tris.reshape(-1, 3).copy() * scale
    if rx_deg != 0:
        a = math.radians(rx_deg)
        c, s = math.cos(a), math.sin(a)
        R = np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float32)
        pts = pts @ R.T
    if ry_deg != 0:
        a = math.radians(ry_deg)
        c, s = math.cos(a), math.sin(a)
        R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float32)
        pts = pts @ R.T
    if rz_deg != 0:
        a = math.radians(rz_deg)
        c, s = math.cos(a), math.sin(a)
        R = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float32)
        pts = pts @ R.T
    pts[:, 0] += tx
    pts[:, 1] += ty
    pts[:, 2] += tz
    return pts.reshape(-1, 3, 3)

def write_binary_stl(filepath, triangles, header_name="AURA_EJUST_RAS_Part"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    header = header_name.encode('ascii')[:80].ljust(80, b' ')
    num_tris = len(triangles)
    with open(filepath, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', num_tris))
        for tri in triangles:
            v0, v1, v2 = tri[0], tri[1], tri[2]
            u = v1 - v0
            v = v2 - v0
            n = np.cross(u, v)
            norm = np.linalg.norm(n)
            n = (n / norm) if norm > 1e-8 else np.array([0.0, 0.0, 1.0], dtype=np.float32)
            f.write(struct.pack('<12fH',
                n[0], n[1], n[2],
                v0[0], v0[1], v0[2],
                v1[0], v1[1], v1[2],
                v2[0], v2[1], v2[2],
                0
            ))

# ==============================================================================
# OFFICIAL E-JUST UNIVERSITY 3D EMBLEM GENERATOR
# ==============================================================================

def create_ejust_university_emblem(cx, cy, cz, scale=1.0, thickness=3.0):
    sun_tris = create_cylinder_along_axis(
        cx, cy, cz + 2.2 * scale, 0.0, 10.2 * scale, thickness, 32, axis='y'
    )

    black_parts = []
    for dx_bar in [-4.0 * scale, 0.0, 4.0 * scale]:
        black_parts.append(create_box_triangles(
            cx + dx_bar, cy, cz + 17.8 * scale, 2.3 * scale, thickness, 6.4 * scale
        ))

    for sign in [-1.0, 1.0]:
        upper_pts = [
            ( 9.5, 17.2, 4.2, 4.5, -22.0),
            (13.2, 13.5, 4.6, 5.2, -45.0),
            (15.6,  8.8, 4.8, 5.5, -68.0),
            (16.6,  4.0, 4.8, 5.2, -84.0),
            (16.6,  0.2, 4.8, 4.2, -90.0),
        ]
        for (ux, uz, wx, wz, ang) in upper_pts:
            b = create_box_triangles(0.0, 0.0, 0.0, wx * scale, thickness, wz * scale)
            black_parts.append(transform_triangles(
                b, ry_deg=sign * ang, tx=cx + sign * ux * scale, ty=cy, tz=cz + uz * scale
            ))

        lower_pts = [
            (16.5, -4.8, 4.8, 4.6,  88.0),
            (15.6, -9.5, 5.0, 5.6,  72.0),
            (13.6,-14.2, 5.2, 6.0,  52.0),
            (10.5,-18.0, 5.4, 6.0,  32.0),
            ( 6.8,-20.4, 5.2, 5.4,  15.0),
            ( 4.2,-21.2, 3.6, 5.2,   0.0),
        ]
        for (lx, lz, wx, wz, ang) in lower_pts:
            b = create_box_triangles(0.0, 0.0, 0.0, wx * scale, thickness, wz * scale)
            black_parts.append(transform_triangles(
                b, ry_deg=sign * ang, tx=cx + sign * lx * scale, ty=cy, tz=cz + lz * scale
            ))

        horn_pts = [
            (12.2, -5.8, 3.6, 2.4, -28.0),
            ( 9.2, -7.4, 3.4, 2.0, -18.0),
        ]
        for (hx, hz, wx, wz, ang) in horn_pts:
            b = create_box_triangles(0.0, 0.0, 0.0, wx * scale, thickness, wz * scale)
            black_parts.append(transform_triangles(
                b, ry_deg=sign * ang, tx=cx + sign * hx * scale, ty=cy, tz=cz + hz * scale
            ))

    return sun_tris, np.concatenate(black_parts, axis=0)

# ==============================================================================
# BIONIC ARTICULATED ARM & 5-FINGER ROBOTIC HAND ENGINE
# ==============================================================================

def create_bionic_hand(is_right=True, pose='welcome'):
    parts = []
    sign = 1.0 if is_right else -1.0

    # Palm body (30mm wide, 28mm tall, 14mm thick)
    parts.append(create_box_triangles(0.0, 0.0, 14.0, 30.0, 14.0, 28.0))
    parts.append(create_box_triangles(0.0, -7.0, 14.0, 26.0, 3.0, 24.0))
    parts.append(create_cylinder_along_axis(0.0, 0.0, 0.0, 0.0, 9.5, 8.0, 20, axis='z'))

    fingers = [
        ("Index",  sign *  8.5, 15.0, 11.0,  9.0, 3.0),
        ("Middle", sign *  2.8, 17.0, 13.0, 10.0, 3.1),
        ("Ring",   sign * -2.8, 15.0, 11.0,  9.0, 3.0),
        ("Pinky",  sign * -8.5, 12.0,  9.0,  7.5, 2.7),
    ]

    bend1 = 12.0 if pose == 'welcome' else 28.0
    bend2 = 18.0 if pose == 'welcome' else 42.0

    for name, bx, l1, l2, l3, r in fingers:
        parts.append(create_ellipsoid(bx, 0.0, 28.0, r * 1.2, r * 1.2, r * 1.2))

        p1 = create_cylinder_along_axis(0.0, 0.0, l1 / 2.0, 0.0, r, l1, 16, axis='z')
        p1_rot = transform_triangles(p1, rx_deg=bend1, tx=bx, ty=0.0, tz=28.0)
        parts.append(p1_rot)

        rad1 = math.radians(bend1)
        k2_y = math.sin(rad1) * l1
        k2_z = 28.0 + math.cos(rad1) * l1
        parts.append(create_ellipsoid(bx, k2_y, k2_z, r * 1.1, r * 1.1, r * 1.1))

        p2 = create_cylinder_along_axis(0.0, 0.0, l2 / 2.0, 0.0, r * 0.9, l2, 16, axis='z')
        p2_rot = transform_triangles(p2, rx_deg=bend1 + bend2, tx=bx, ty=k2_y, tz=k2_z)
        parts.append(p2_rot)

        rad2 = math.radians(bend1 + bend2)
        tip_y = k2_y + math.sin(rad2) * l2
        tip_z = k2_z + math.cos(rad2) * l2
        parts.append(create_ellipsoid(bx, tip_y, tip_z, r * 0.8, r * 0.8, r * 0.8))

    # Opposable Thumb
    thumb_x = sign * 16.0
    thumb_y = 2.0
    thumb_z = 9.0
    parts.append(create_ellipsoid(thumb_x, thumb_y, thumb_z, 4.0, 4.0, 4.0))

    t1 = create_cylinder_along_axis(0.0, 0.0, 7.5, 0.0, 3.2, 15.0, 16, axis='z')
    t1_rot = transform_triangles(t1, rx_deg=25.0, ry_deg=sign * 35.0, tx=thumb_x, ty=thumb_y, tz=thumb_z)
    parts.append(t1_rot)

    t_end_x = thumb_x + math.sin(math.radians(sign * 35.0)) * 15.0
    t_end_y = thumb_y + math.sin(math.radians(25.0)) * 15.0
    t_end_z = thumb_z + math.cos(math.radians(25.0)) * math.cos(math.radians(sign * 35.0)) * 15.0
    parts.append(create_ellipsoid(t_end_x, t_end_y, t_end_z, 3.0, 3.0, 3.0))

    t2 = create_cylinder_along_axis(0.0, 0.0, 5.5, 0.0, 2.8, 11.0, 16, axis='z')
    t2_rot = transform_triangles(t2, rx_deg=35.0, ry_deg=sign * 15.0, tx=t_end_x, ty=t_end_y, tz=t_end_z)
    parts.append(t2_rot)

    return np.concatenate(parts, axis=0)

def create_sculpted_arm_segment(length, r_top, r_bot, segments=32):
    zs = np.linspace(0, length, 10)
    slices = []
    for z in zs:
        frac = z / length
        bulge = 1.0 + 0.20 * math.sin(frac * math.pi)
        r = (r_top * (1.0 - frac) + r_bot * frac) * bulge
        slices.append((z, r))

    tris = []
    angles = np.linspace(0, 2*np.pi, segments, endpoint=False)
    for i in range(len(slices) - 1):
        z0, r0 = slices[i]
        z1, r1 = slices[i+1]
        for j in range(segments):
            jnext = (j + 1) % segments
            a0, a1 = angles[j], angles[jnext]
            p00 = [r0 * math.cos(a0), r0 * math.sin(a0), z0]
            p01 = [r0 * math.cos(a1), r0 * math.sin(a1), z0]
            p10 = [r1 * math.cos(a0), r1 * math.sin(a0), z1]
            p11 = [r1 * math.cos(a1), r1 * math.sin(a1), z1]
            tris.append([p00, p01, p11])
            tris.append([p00, p11, p10])
    return np.array(tris, dtype=np.float32)

def build_full_articulated_arm_colored(is_right=True, pose='welcome'):
    PEARL_WHITE = (0.94, 0.95, 0.98)
    CARBON_DARK = (0.12, 0.12, 0.16)

    colored_groups = []
    sign = 1.0 if is_right else -1.0

    # Upper arm (length 115mm)
    upper = create_sculpted_arm_segment(115.0, 21.0, 17.0)
    colored_groups.append((upper, PEARL_WHITE))

    # Elbow joint (at Z = 115mm)
    elbow_hub = create_cylinder_along_axis(0.0, 0.0, 115.0, 7.0, 17.0, 24.0, 28, axis='x')
    elbow_caps = create_cylinder_along_axis(0.0, 0.0, 115.0, 0.0, 11.0, 26.0, 20, axis='x')
    colored_groups.append((np.concatenate([elbow_hub, elbow_caps], axis=0), CARBON_DARK))

    # Forearm (length 110mm)
    forearm = create_sculpted_arm_segment(110.0, 17.0, 13.0)
    wrist_hub = create_cylinder_along_axis(0.0, 0.0, 110.0, 0.0, 11.0, 12.0, 24, axis='z')
    hand = create_bionic_hand(is_right=is_right, pose=pose)
    hand_placed = transform_triangles(hand, tx=0.0, ty=0.0, tz=112.0)

    forearm_white = np.concatenate([forearm, hand_placed], axis=0)
    forearm_dark = wrist_hub

    if pose == 'welcome':
        fw_bent = transform_triangles(forearm_white, rx_deg=46.0, rz_deg=-sign*15.0, tz=115.0)
        fd_bent = transform_triangles(forearm_dark, rx_deg=46.0, rz_deg=-sign*15.0, tz=115.0)
    else:
        fw_bent = transform_triangles(forearm_white, rx_deg=14.0, tz=115.0)
        fd_bent = transform_triangles(forearm_dark, rx_deg=14.0, tz=115.0)

    colored_groups.append((fw_bent, PEARL_WHITE))
    colored_groups.append((fd_bent, CARBON_DARK))

    all_arm_tris = np.concatenate([g[0] for g in colored_groups], axis=0)
    return all_arm_tris, colored_groups

# ==============================================================================
# COMPONENT-FIT PART GENERATORS (ALL Z-UP, +Y FRONT, <= 220mm BUILD PLATE)
# ==============================================================================

def generate_part_01_aero_drive_base():
    """
    01_Drive_Base_Chassis.stl (216.0 x 216.0 x 66.0 mm, Z = 0..66mm, +Y = Front)
    Aerodynamic concept supercar rover chassis with 4 flared wheel arches, front chin spoiler,
    recessed horizontal sensor pod, and pairwise-disjoint internal component bays.
    """
    parts = []

    # 1. Sculpted Aerodynamic Supercar Rover Shroud (Z = 0..46mm)
    base_slices = [
        ( 0.0, 0.0,  0.0, 106.0, 106.0, 3.2),
        ( 8.0, 0.0,  0.0, 107.5, 107.5, 3.0),
        (20.0, 0.0, -1.5, 104.0, 103.0, 2.7),
        (34.0, 0.0, -3.0,  95.0,  95.0, 2.4),
        (46.0, 0.0, -4.0,  84.0,  85.0, 2.2),
    ]
    parts.append(create_lofted_shell(base_slices, wall_thickness=4.5, segments=56, cap_bottom=False, cap_top=False))

    # 2. 4 Swept Futuristic Wheel Fender Blister Flares (Front X=±84, Y=+58; Rear X=±84, Y=-58)
    for sign_x in [-1.0, 1.0]:
        for y_arch in [58.0, -58.0]:
            fender = create_cylinder_along_axis(sign_x * 84.0, y_arch, 18.0, 38.0, 45.0, 32.0, 32, axis='x')
            mask = fender[:, :, 2].mean(axis=1) >= 6.0
            parts.append(fender[mask])

    # 3. Aerodynamic Front Chin Splitter & Recessed Sensor Fascia (Z = 0..24mm, Y = +94..+106mm)
    parts.append(create_box_triangles(0.0, 98.0, 6.0, 128.0, 16.0, 12.0))
    parts.append(create_cylinder_along_axis(-32.0, 104.0, 18.0, 8.2, 11.5, 12.0, 24, axis='y'))
    parts.append(create_cylinder_along_axis( 32.0, 104.0, 18.0, 8.2, 11.5, 12.0, 24, axis='y'))

    # 4. Structural Internal Chassis Deck (Z = 0..6.0mm) with Open Front Optical Window
    parts.append(create_box_triangles(  0.0, -12.0, 3.0, 146.0, 190.0, 6.0))
    parts.append(create_box_triangles(-62.0,  95.0, 3.0,  24.0,  22.0, 6.0))
    parts.append(create_box_triangles( 62.0,  95.0, 3.0,  24.0,  22.0, 6.0))

    # 5. Dual Vertical Ø25.4mm Spine Sockets (X = ±45.0mm, Y = -14.5mm, OD 32.0mm, ID 25.4mm, Z = 0..66mm)
    parts.append(create_cylinder_along_axis(-45.0, -14.5, 33.0, 12.7, 16.0, 66.0, 40, axis='z'))
    parts.append(create_cylinder_along_axis( 45.0, -14.5, 33.0, 12.7, 16.0, 66.0, 40, axis='z'))
    parts.append(create_box_triangles(0.0, -14.5, 30.0, 58.0, 10.0, 48.0))
    parts.append(create_cylinder_along_axis(0.0, -14.5, 32.0, 9.0, 13.0, 52.0, 28, axis='z'))

    # 6. Disjoint JGA25-370 12V Gearmotor Cradles & Faceplates (Y = +16.5mm, X = ±45.0mm, Z = 22mm)
    for sign in [-1.0, 1.0]:
        parts.append(create_box_triangles(sign * 71.0, 16.5, 24.0, 6.0, 29.0, 36.0))
        cradle = create_cylinder_along_axis(sign * 45.0, 16.5, 22.0, 12.8, 14.5, 52.0, 28, axis='x')
        mask_c = cradle[:, :, 2].mean(axis=1) <= 23.0
        parts.append(cradle[mask_c])
        parts.append(create_cylinder_along_axis(sign * 74.0, 16.5, 22.0, 3.6, 8.0, 6.0, 24, axis='x'))

    # 7. Dedicated Component Bays:
    # 7a. 3S 18650 Battery Tray (74.0 x 58.0 x 22.0 mm at X=0, Y=-63.0mm)
    parts.append(create_walled_pocket(0.0, -63.0, 6.0, 74.0, 58.0, 22.0, wall_t=2.8))
    # 7b. Dual LM2596 Buck Bays (24.0 x 46.0 x 12.0 mm at X = ±58.0mm, Y = -58.0mm)
    parts.append(create_walled_pocket(-58.0, -58.0, 6.0, 24.0, 46.0, 12.0, wall_t=2.4, standoffs=[(-8.0, -15.0, 6.0), (8.0, 15.0, 6.0)]))
    parts.append(create_walled_pocket( 58.0, -58.0, 6.0, 24.0, 46.0, 12.0, wall_t=2.4, standoffs=[(-8.0, -15.0, 6.0), (8.0, 15.0, 6.0)]))
    # 7c. Front L298N Motor Driver Bay (46.0 x 46.0 x 12.0 mm at X=0, Y=+57.0mm)
    l298_standoffs = [(-18.5, -18.5, 8.0), (18.5, -18.5, 8.0), (-18.5, 18.5, 8.0), (18.5, 18.5, 8.0)]
    parts.append(create_walled_pocket(0.0, 57.0, 6.0, 46.0, 46.0, 12.0, wall_t=2.6, standoffs=l298_standoffs))

    # 8. Front Optical 5-Channel TCRT5000 IR Sensor Channel (98.0 x 22.0 x 10.0 mm at X=0, Y=+96.5mm)
    parts.append(create_walled_pocket(0.0, 96.5, 6.0, 98.0, 22.0, 10.0, wall_t=2.4, standoffs=[(-35.0, 0.0, 6.0), (35.0, 0.0, 6.0)]))

    # 9. Disjoint Ball Caster Mounting Bosses
    parts.append(create_cylinder_along_axis(-44.0,  57.0, 4.0, 4.0, 13.0, 8.0, 24, axis='z'))
    parts.append(create_cylinder_along_axis( 44.0,  57.0, 4.0, 4.0, 13.0, 8.0, 24, axis='z'))
    parts.append(create_cylinder_along_axis(-52.0, -94.5, 4.0, 4.0, 10.0, 8.0, 24, axis='z'))
    parts.append(create_cylinder_along_axis( 52.0, -94.5, 4.0, 4.0, 10.0, 8.0, 24, axis='z'))

    # 10. Rear Power Switch & DC Barrel Jack Bezel at Y = -104mm
    parts.append(create_box_triangles(-16.0, -104.0, 22.0, 26.0, 8.0, 19.0))
    parts.append(create_cylinder_along_axis(18.0, -104.0, 22.0, 4.1, 8.5, 8.0, 24, axis='y'))

    return np.concatenate(parts, axis=0)

def generate_part_02_sculpted_torso_nfc(include_emblems=True):
    """
    02_Torso_NFC_Badge_Dock.stl (196.0 x 106.0 x 180.0 mm, Z = 0..180mm, +Y = Front Chest)
    Athletic V-Tapered Bionic Chest Armor + Shield-Shaped Smartphone Kiosk Dock (166x82x11.5mm)
    + Lower Illuminated Circular NFC Halo (OD 62mm) + Internal MFRC522 Pocket + Disjoint Spine Electronics.
    """
    parts = []

    # 1. Athletic V-Tapered Torso Armor Shell (Lofted along Z = 0..180mm)
    torso_slices = [
        (  0.0, 0.0, -3.0, 68.0, 33.0, 2.3),
        ( 38.0, 0.0, -1.0, 78.0, 34.0, 2.5),
        ( 82.0, 0.0,  0.0, 89.0, 35.0, 2.7),
        (132.0, 0.0,  0.0, 97.0, 35.5, 2.8),
        (162.0, 0.0, -1.0, 86.0, 34.0, 2.5),
        (180.0, 0.0, -3.0, 64.0, 29.0, 2.2),
    ]
    parts.append(create_lofted_shell(torso_slices, wall_thickness=4.0, segments=52, cap_bottom=False, cap_top=False))

    # 2. Dual Internal Ø25.4mm Vertical Spine Clamp Sleeves (X = ±45mm, Y = -14.5mm, Z = 0..176mm)
    parts.append(create_cylinder_along_axis(-45.0, -14.5, 88.0, 12.7, 18.0, 176.0, 36, axis='z'))
    parts.append(create_cylinder_along_axis( 45.0, -14.5, 88.0, 12.7, 18.0, 176.0, 36, axis='z'))

    # 3. Disjoint Internal Torso Electronics Mounting Bridge
    parts.append(create_box_triangles(0.0, -14.5, 92.0, 56.0, 6.0, 162.0))
    # 3a. Top: ESP32 Cradle (31.0 x 58.0 x 12.0 mm at Z = 136mm)
    parts.append(transform_triangles(
        create_walled_pocket(0.0, 0.0, 0.0, 31.0, 58.0, 12.0, wall_t=2.4, standoffs=[(-12.0, -24.0, 6.0), (12.0, 24.0, 6.0)]),
        rx_deg=90.0, tx=0.0, ty=-17.5, tz=136.0
    ))
    # 3b. Middle: DFPlayer Bay (23.0 x 23.0 x 10.0 mm at Z = 82mm)
    parts.append(transform_triangles(
        create_walled_pocket(0.0, 0.0, 0.0, 23.0, 23.0, 10.0, wall_t=2.2),
        rx_deg=90.0, tx=0.0, ty=-17.5, tz=82.0
    ))
    # 3c. Bottom: Ø40mm Speaker Chamber (Z = 36mm)
    parts.append(create_cylinder_along_axis(0.0, -9.5, 36.0, 20.5, 23.0, 16.0, 32, axis='y'))

    # 4. Front Interactive Shield Kiosk Console on +Y Face (Tilted -8° toward standing guests)
    console = []
    console.append(create_box_triangles(0.0, 0.0, 4.0, 174.0, 5.0, 150.0))

    # Upper Smartphone Pocket (166.0 x 82.0 x 11.5 mm, Z = +37mm)
    console.append(create_box_triangles(0.0, 8.25, -6.0, 174.0, 11.5, 4.0))
    console.append(create_box_triangles(-76.0, 8.25, 80.0, 22.0, 11.5, 4.0))
    console.append(create_box_triangles( 76.0, 8.25, 80.0, 22.0, 11.5, 4.0))
    console.append(create_box_triangles(-85.0, 8.25, 37.0, 4.0, 11.5, 86.0))
    console.append(create_box_triangles( 85.0, 8.25, 61.5, 4.0, 11.5, 37.0))
    console.append(create_box_triangles( 85.0, 8.25, 12.5, 4.0, 11.5, 37.0))
    console.append(create_box_triangles(  0.0, 14.5, -3.5, 174.0, 2.0, 5.0))
    console.append(create_box_triangles(-76.0, 14.5, 77.5,  22.0, 2.0, 5.0))
    console.append(create_box_triangles( 76.0, 14.5, 77.5,  22.0, 2.0, 5.0))
    console.append(create_box_triangles(-81.0, 14.5, 37.0,   8.0, 2.0, 82.0))
    console.append(create_box_triangles( 81.0, 14.5, 37.0,   8.0, 2.0, 82.0))

    # Lower Circular NFC Tap Halo Ring (OD 62mm, ID 48mm at Z = -39mm)
    console.append(create_cylinder_along_axis(0.0, 5.0, -39.0, 24.0, 31.0, 6.0, 40, axis='y'))
    if include_emblems:
        nfc_sun, nfc_arcs = create_ejust_university_emblem(0.0, 5.5, -39.0, scale=0.72, thickness=6.0)
        console.append(nfc_sun)
        console.append(nfc_arcs)
        pect_sun, pect_arcs = create_ejust_university_emblem(58.0, 5.0, -36.0, scale=0.62, thickness=5.0)
        console.append(pect_sun)
        console.append(pect_arcs)

    # Internal MFRC522 pocket (42.0 x 62.0 x 7.0 mm) behind 1.5mm RF wall
    console.append(create_box_triangles(-22.5, -4.5, -39.0, 3.0, 7.0, 62.0))
    console.append(create_box_triangles( 22.5, -4.5, -39.0, 3.0, 7.0, 62.0))
    console.append(create_box_triangles(  0.0, -4.5,  -6.5, 48.0, 7.0, 3.0))
    console.append(create_box_triangles(  0.0, -4.5, -71.5, 48.0, 7.0, 3.0))
    console.append(create_box_triangles(0.0, 6.5, -68.0, 88.0, 9.0, 5.0))

    # Flank intake vent ribs
    for z_fin in [-50.0, -36.0, -22.0]:
        console.append(create_box_triangles(-59.0, 4.0, z_fin, 22.0, 4.0, 4.0))

    console_mesh = np.concatenate(console, axis=0)
    parts.append(transform_triangles(console_mesh, rx_deg=-8.0, ty=39.0, tz=90.0))

    return np.concatenate(parts, axis=0)

def generate_part_03_bionic_head_visor(include_emblem=True):
    """
    03_Humanoid_Head_Shell.stl (172.0 x 136.0 x 142.0 mm, Z = 0..142mm, +Y = Front Face)
    Aerodynamic Android Helmet Dome + Panoramic Cyber-Visor Recess + Dual Circular Eye Bezels
    + Rotary Ear Turbines + Sagittal Cranial Crest Fin + Official E-JUST Forehead Crest.
    """
    parts = []

    # 1. MG996R Neck Pan Gimbal Collar (Z = 0..24mm)
    parts.append(create_cylinder_along_axis(0.0, -4.0, 12.0, 14.0, 27.0, 24.0, 36, axis='z'))
    parts.append(create_cylinder_along_axis(0.0, -4.0, 6.0, 10.0, 14.5, 12.0, 28, axis='z'))

    # 2. Sleek Aerodynamic Helmet Dome (Lofted along Z = 16..136mm)
    head_slices = [
        ( 16.0, 0.0, -2.0, 52.0, 48.0, 2.1),
        ( 38.0, 0.0,  4.0, 68.0, 58.0, 2.2),
        ( 68.0, 0.0,  8.0, 76.0, 64.0, 2.3),
        ( 96.0, 0.0,  6.0, 77.0, 65.0, 2.3),
        (118.0, 0.0,  0.0, 68.0, 58.0, 2.1),
        (132.0, 0.0, -4.0, 48.0, 42.0, 2.0),
        (136.0, 0.0, -6.0, 24.0, 22.0, 2.0),
    ]
    parts.append(create_lofted_shell(head_slices, wall_thickness=4.0, segments=52, cap_bottom=True, cap_top=True))

    # 3. Seamless Panoramic Wrap-Around Cyber-Visor Frame (Z = 56..104mm)
    visor_slices = [
        ( 56.0, 0.0, 12.0, 67.0, 56.0, 2.3),
        ( 79.0, 0.0, 15.0, 71.0, 60.0, 2.4),
        (104.0, 0.0, 11.0, 65.0, 54.0, 2.3),
    ]
    parts.append(create_lofted_shell(visor_slices, wall_thickness=3.5, segments=48, cap_bottom=False, cap_top=False))

    # 4. Dual Expressive Circular Eye Bezels (X = ±28mm, Z = 80mm)
    for sign in [-1.0, 1.0]:
        parts.append(transform_triangles(
            create_cylinder_along_axis(0.0, 0.0, 0.0, 11.0, 18.5, 10.0, 36, axis='y'),
            rz_deg=-sign * 8.0, tx=sign * 28.0, ty=66.0, tz=80.0
        ))
        parts.append(create_box_triangles(sign * 22.0, 18.0, 88.0, 34.0, 5.0, 3.0))
        parts.append(create_box_triangles(sign * 22.0, 18.0, 68.0, 34.0, 5.0, 3.0))

    # 5. Rotary Mechatronic Ear Turbines (X = ±78mm, Y = 0, Z = 76mm)
    for sign in [-1.0, 1.0]:
        parts.append(create_cylinder_along_axis(sign * 77.0, 0.0, 76.0, 0.0, 25.0, 12.0, 32, axis='x'))
        parts.append(create_cylinder_along_axis(sign * 83.0, 0.0, 76.0, 16.0, 23.0, 6.0, 32, axis='x'))

    # 6. Sagittal Aerodynamic Cranial Crest Fin along Top Centerline (Z = 120..142mm)
    parts.append(create_box_triangles(0.0, -4.0, 132.0, 9.0, 64.0, 20.0))
    if include_emblem:
        head_sun, head_arcs = create_ejust_university_emblem(0.0, 0.0, 0.0, scale=0.68, thickness=8.0)
        parts.append(transform_triangles(head_sun, rx_deg=30.0, tx=0.0, ty=64.0, tz=112.0))
        parts.append(transform_triangles(head_arcs, rx_deg=30.0, tx=0.0, ty=64.0, tz=112.0))

    return np.concatenate(parts, axis=0)

def generate_part_04_bionic_shoulder():
    """
    04_Shoulder_Arm_Bracket.stl (132.0 x 68.0 x 56.0 mm, Z = 0..56mm)
    Sculpted Bionic Pauldron Armor Dome & Precision MG996R Servo Actuator Cradle (41.2 x 20.6 x 42.0 mm)
    + Ø25.4mm Spine Clamp Collar.
    """
    parts = []
    parts.append(create_cylinder_along_axis(0.0, 0.0, 26.0, 12.7, 18.5, 52.0, 36, axis='z'))
    parts.append(create_box_triangles(22.0, 0.0, 26.0, 16.0, 14.0, 52.0))

    pauldron_slices = [
        ( 0.0, 58.0, 0.0, 44.0, 28.0, 2.3),
        (18.0, 62.0, 0.0, 52.0, 34.0, 2.5),
        (38.0, 58.0, 0.0, 48.0, 32.0, 2.4),
        (56.0, 54.0, 0.0, 38.0, 25.0, 2.2),
    ]
    parts.append(create_lofted_shell(pauldron_slices, wall_thickness=4.0, segments=40, cap_bottom=False, cap_top=False))

    parts.append(create_box_triangles(62.0,  12.8, 21.0, 46.2, 5.0, 42.0))
    parts.append(create_box_triangles(62.0, -12.8, 21.0, 46.2, 5.0, 42.0))
    parts.append(create_box_triangles(38.9,   0.0, 21.0,  5.0, 25.6, 42.0))
    parts.append(create_box_triangles(85.1,   0.0, 21.0,  5.0, 25.6, 42.0))
    parts.append(create_cylinder_along_axis(37.25, 0.0, 32.0, 2.0, 5.0, 14.0, 20, axis='z'))
    parts.append(create_cylinder_along_axis(86.75, 0.0, 32.0, 2.0, 5.0, 14.0, 20, axis='z'))

    return np.concatenate(parts, axis=0)

def generate_part_05_spine_fairing_ring():
    """
    05_Spine_Aero_Fairing_Ring.stl (148.0 x 100.0 x 36.0 mm, Z = 0..36mm)
    Segmented Bionic Toroidal Vertebra Ring with Dual Ø25.4mm Spine Bores + Central Ø22mm Harness Conduit
    + Lateral Aerodynamic Cooling Vent Gills.
    """
    parts = []
    ring_slices = [
        ( 0.0, 0.0, 0.0, 70.0, 47.0, 2.3),
        (18.0, 0.0, 1.5, 74.0, 50.0, 2.5),
        (36.0, 0.0, 0.0, 70.0, 47.0, 2.3),
    ]
    parts.append(create_lofted_shell(ring_slices, wall_thickness=3.5, segments=48, cap_bottom=False, cap_top=False))

    parts.append(create_cylinder_along_axis(-45.0, -14.5, 18.0, 12.7, 18.0, 36.0, 32, axis='z'))
    parts.append(create_cylinder_along_axis( 45.0, -14.5, 18.0, 12.7, 18.0, 36.0, 32, axis='z'))
    parts.append(create_box_triangles(0.0, -14.5, 18.0, 58.0, 6.0, 32.0))
    parts.append(create_cylinder_along_axis(0.0, -14.5, 18.0, 11.0, 15.0, 36.0, 28, axis='z'))

    for sign in [-1.0, 1.0]:
        for z_gill in [10.0, 18.0, 26.0]:
            parts.append(create_box_triangles(sign * 68.0, 0.0, z_gill, 4.0, 24.0, 3.5))

    return np.concatenate(parts, axis=0)

def generate_part_07_tft35_adapter_bezel():
    """
    07_TFT_35_Adapter_Bezel.stl (165.0 x 81.0 x 9.0 mm, Z = 0..9mm)
    Drop-in adapter frame (+1.0mm slip fit into the 166x82mm smartphone dock) converting it to hold 3.5" SPI TFT.
    """
    parts = []
    parts.append(create_box_triangles(0.0,  27.75, 2.0, 165.0, 25.5, 4.0))
    parts.append(create_box_triangles(0.0, -27.75, 2.0, 165.0, 25.5, 4.0))
    parts.append(create_box_triangles(-61.25, 0.0, 2.0,  42.5, 30.0, 4.0))
    parts.append(create_box_triangles( 61.25, 0.0, 2.0,  42.5, 30.0, 4.0))
    standoffs = [(-45.5, -25.5, 5.0), (45.5, -25.5, 5.0), (-45.5, 25.5, 5.0), (45.5, 25.5, 5.0)]
    parts.append(create_walled_pocket(0.0, 0.0, 4.0, 98.5, 58.5, 5.0, wall_t=2.5, standoffs=standoffs))
    return np.concatenate(parts, axis=0)

# ==============================================================================
# HIGH-FIDELITY SHOWCASE ASSEMBLY MATCHING IEEE_RAS_EJUST_Humanoid_Showcase.jpg
# ==============================================================================

def generate_part_06_full_assembly_colored(p01, p02, p03, p04, p05):
    """
    Constructs the master humanoid robot reference assembly matching
    the exact proportions and automotive styling of IEEE_RAS_EJUST_Humanoid_Showcase.jpg:
      - Rover Base with 4 Flared Wheel Arches & Front Sensor Pod: Z = 0..120mm
      - 4 Chunky Rubber Wheels with Glowing Magenta Rim Halos (OD 96mm, width 32mm)
      - Segmented Bionic Spine with 4 Stacked Toroidal Vertebrae Rings: Z = 120..310mm
      - Athletic V-Tapered Torso with Shield Kiosk Screen & NFC Halo: Z = 310..580mm
      - Bionic Shoulders with Spherical Pauldron Domes: Z = 550mm
      - Articulated Bionic Arms with 5-Finger Robotic Hands (Welcoming Right Arm Gesture!)
      - Ribbed Bionic Neck Column: Z = 580..630mm
      - Aerodynamic Cyber-Visor Android Helmet Dome with Glowing Eyes: Z = 630..815mm
    """
    PEARL_WHITE   = (0.94, 0.95, 0.98) # Satin Pearl Titanium White Body Armor
    CRIMSON_WEAVE = (0.75, 0.08, 0.28) # Official E-JUST / RAS Crimson Armor Weave
    RAS_PURPLE    = (0.42, 0.08, 0.48) # Official IEEE RAS Royal Purple
    MAGENTA_GLOW  = (1.00, 0.10, 0.55) # Glowing Neon Magenta LEDs (Wheels, Eyes, NFC Halo)
    PHONE_SCREEN  = (0.08, 0.04, 0.12) # AMOLED Dark Glass Display
    CARBON_DARK   = (0.10, 0.10, 0.14) # Obsidian Carbon Tires, Spine & Neck

    groups = []

    # 1. Rover Base Pod at Z = 24mm (Pearl White with Crimson Accents)
    groups.append((transform_triangles(p01, tz=24.0), PEARL_WHITE))

    # 2. 4 Chunky Rubber Wheels with Glowing Magenta Circular Rim Halos (Z = 48mm)
    # Front wheels at Y = +58mm, Rear wheels at Y = -58mm, X = ±84mm
    for sign_x in [-1.0, 1.0]:
        for y_pos in [58.0, -58.0]:
            # Chunky black rubber tire (OD 92mm, width 30mm)
            tire = create_cylinder_along_axis(sign_x * 84.0, y_pos, 48.0, 16.0, 46.0, 28.0, 32, axis='x')
            groups.append((tire, CARBON_DARK))
            # Glowing neon magenta rim halo ring on outer wheel face (OD 68mm, ID 52mm)
            rim_outer_x = sign_x * (84.0 + 14.5)
            halo = create_cylinder_along_axis(rim_outer_x, y_pos, 48.0, 26.0, 34.0, 2.5, 32, axis='x')
            groups.append((halo, MAGENTA_GLOW))

    # Front stereo camera / sensor optics inside front pod (Y = +128mm, Z = 42mm)
    groups.append((create_cylinder_along_axis(-32.0, 128.0, 42.0, 0.0, 8.0, 4.0, 24, axis='y'), MAGENTA_GLOW))
    groups.append((create_cylinder_along_axis( 32.0, 128.0, 42.0, 0.0, 8.0, 4.0, 24, axis='y'), MAGENTA_GLOW))

    # 3. Central Dark Carbon Spine Columns (Z = 50..320mm)
    groups.append((create_cylinder_along_axis(0.0, -14.5, 185.0, 22.0, 27.0, 270.0, 32, axis='z'), CARBON_DARK))
    groups.append((create_cylinder_along_axis(-45.0, -14.5, 185.0, 10.5, 12.7, 270.0, 24, axis='z'), CARBON_DARK))
    groups.append((create_cylinder_along_axis( 45.0, -14.5, 185.0, 10.5, 12.7, 270.0, 24, axis='z'), CARBON_DARK))

    # 4. 4 Stacked Bionic Toroidal Vertebrae Rings with Deep 12mm Shadow Reveals (Z = 135, 180, 225, 270 mm)
    vert_colors = [CRIMSON_WEAVE, RAS_PURPLE, CRIMSON_WEAVE, RAS_PURPLE]
    for z_vert, v_col in zip([135.0, 180.0, 225.0, 270.0], vert_colors):
        v_torus = create_torus(0.0, -14.5, z_vert, 52.0, 15.0, segments_u=44, segments_v=24, scale_x=1.35, scale_y=0.95)
        groups.append((v_torus, v_col))

    # 5. Sculpted Athletic V-Tapered Torso at Z = 310..490mm (Pearl White & Side Crimson Flank Armor)
    p02_base = generate_part_02_sculpted_torso_nfc(include_emblems=False)
    groups.append((transform_triangles(p02_base, tz=310.0), PEARL_WHITE))

    # Side rib flank armor panels (Crimson Weave)
    flank_l = create_box_triangles(-76.0, 8.0, 385.0, 16.0, 48.0, 92.0)
    flank_r = create_box_triangles( 76.0, 8.0, 385.0, 16.0, 48.0, 92.0)
    groups.append((flank_l, CRIMSON_WEAVE))
    groups.append((flank_r, CRIMSON_WEAVE))

    # AMOLED Chest Kiosk Screen (Z = 437mm, tilted -8°)
    screen_slab = create_box_triangles(0.0, 18.0, 37.0, 150.0, 2.5, 68.0)
    groups.append((transform_triangles(screen_slab, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), PHONE_SCREEN))

    # Glowing Magenta Circular NFC Tap Halo (Z = 361mm)
    nfc_ring = create_cylinder_along_axis(0.0, 9.5, -39.0, 23.0, 31.0, 3.5, 36, axis='y')
    groups.append((transform_triangles(nfc_ring, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), MAGENTA_GLOW))

    # Official E-JUST University 3D Crest inside NFC Halo
    nfc_sun, nfc_arcs = create_ejust_university_emblem(0.0, 5.5, -39.0, scale=0.72, thickness=6.0)
    groups.append((transform_triangles(nfc_sun, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), CRIMSON_WEAVE))
    groups.append((transform_triangles(nfc_arcs, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), CARBON_DARK))

    # Event VIP Badge Card tapping at the NFC Halo
    badge_card = create_box_triangles(16.0, 18.0, -32.0, 54.0, 1.2, 85.0)
    groups.append((transform_triangles(badge_card, rx_deg=-8.0, rz_deg=22.0, ty=39.0, tz=90.0 + 310.0), CARBON_DARK))

    # Official E-JUST Crest on Left Chest & IEEE RAS Badge on Right Chest
    pect_sun, pect_arcs = create_ejust_university_emblem(58.0, 5.0, -36.0, scale=0.62, thickness=5.0)
    groups.append((transform_triangles(pect_sun, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), CRIMSON_WEAVE))
    groups.append((transform_triangles(pect_arcs, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), CARBON_DARK))
    ras_badge = create_cylinder_along_axis(-58.0, 5.0, -36.0, 0.0, 14.0, 5.0, 28, axis='y')
    groups.append((transform_triangles(ras_badge, rx_deg=-8.0, ty=39.0, tz=90.0 + 310.0), RAS_PURPLE))

    # 6. Shoulder Pauldron Domes at Z = 445mm (Spherical Crimson/Purple Armor)
    pauldron_l = create_ellipsoid(-106.0, -14.5, 445.0, 42.0, 36.0, 30.0)
    pauldron_r = create_ellipsoid( 106.0, -14.5, 445.0, 42.0, 36.0, 30.0)
    groups.append((pauldron_l, RAS_PURPLE))
    groups.append((pauldron_r, CRIMSON_WEAVE))

    # 7. Articulated Bionic Arms with 5-Finger Robotic Hands
    # RIGHT ARM: Dynamically raised forward & upward in a welcoming VIP greeting gesture!
    _, r_arm_groups = build_full_articulated_arm_colored(is_right=True, pose='welcome')
    for g_tris, g_col in r_arm_groups:
        placed_tris = transform_triangles(
            g_tris, rx_deg=-65.0, ry_deg=24.0, rz_deg=-15.0, tx=108.0, ty=10.0, tz=445.0
        )
        groups.append((placed_tris, g_col))

    # LEFT ARM: Relaxed naturally beside the left hip
    _, l_arm_groups = build_full_articulated_arm_colored(is_right=False, pose='relaxed')
    for g_tris, g_col in l_arm_groups:
        placed_tris = transform_triangles(
            g_tris, rx_deg=172.0, ry_deg=-8.0, tx=-108.0, ty=4.0, tz=445.0
        )
        groups.append((placed_tris, g_col))

    # 8. Exposed Ribbed Bionic Neck Column (Z = 490..535mm)
    groups.append((create_cylinder_along_axis(0.0, -4.0, 512.5, 18.0, 24.0, 45.0, 32, axis='z'), CARBON_DARK))

    # 9. Futuristic Cyber-Visor Android Helmet Dome at Z = 530..672mm
    p03_base = generate_part_03_bionic_head_visor(include_emblem=False)
    groups.append((transform_triangles(p03_base, tz=530.0), PEARL_WHITE))

    # Seamless Panoramic Wrap-Around Gloss-Black Visor
    visor_glass = create_ellipsoid(0.0, 22.0, 608.0, 62.0, 46.0, 32.0)
    mask_vg = visor_glass[:, :, 1].mean(axis=1) >= 20.0
    groups.append((visor_glass[mask_vg], CARBON_DARK))

    # Dual Glowing Neon Magenta Circular Eye Rings shining from behind the visor
    eye_l = create_cylinder_along_axis(-28.0, 72.0, 610.0, 11.0, 18.0, 3.5, 32, axis='y')
    eye_r = create_cylinder_along_axis( 28.0, 72.0, 610.0, 11.0, 18.0, 3.5, 32, axis='y')
    pupil_l = create_cylinder_along_axis(-28.0, 73.0, 610.0, 0.0, 5.0, 4.0, 20, axis='y')
    pupil_r = create_cylinder_along_axis( 28.0, 73.0, 610.0, 0.0, 5.0, 4.0, 20, axis='y')
    groups.append((np.concatenate([eye_l, pupil_l], axis=0), MAGENTA_GLOW))
    groups.append((np.concatenate([eye_r, pupil_r], axis=0), MAGENTA_GLOW))

    # Official E-JUST Crest on Sloped Forehead
    head_sun, head_arcs = create_ejust_university_emblem(0.0, 0.0, 0.0, scale=0.68, thickness=8.0)
    groups.append((transform_triangles(head_sun, rx_deg=30.0, tx=0.0, ty=64.0, tz=112.0 + 530.0), CRIMSON_WEAVE))
    groups.append((transform_triangles(head_arcs, rx_deg=30.0, tx=0.0, ty=64.0, tz=112.0 + 530.0), CARBON_DARK))

    # Cranial crest fin highlight in crimson
    crest_fin = create_box_triangles(0.0, -4.0, 664.0, 8.0, 62.0, 18.0)
    groups.append((crest_fin, CRIMSON_WEAVE))

    all_tris = np.concatenate([g[0] for g in groups], axis=0)
    return all_tris, groups

# ==============================================================================
# PHONG-SHADED STUDIO CAD RENDERER (7-PANEL COMPLETE BLUEPRINT)
# ==============================================================================

def compute_phong_colors(triangles, base_rgb, light_dir=(0.45, 0.72, 0.68), rim_dir=(-0.6, 0.4, 0.5)):
    v0 = triangles[:, 0, :]
    v1 = triangles[:, 1, :]
    v2 = triangles[:, 2, :]
    normals = np.cross(v1 - v0, v2 - v0)
    norms = np.linalg.norm(normals, axis=1, keepdims=True)
    valid = (norms > 1e-8).squeeze()
    normals[valid] = normals[valid] / norms[valid]
    normals[~valid] = np.array([0.0, 0.0, 1.0], dtype=np.float32)

    L = np.array(light_dir, dtype=np.float32)
    L = L / np.linalg.norm(L)
    R_dir = np.array(rim_dir, dtype=np.float32)
    R_dir = R_dir / np.linalg.norm(R_dir)
    V = np.array([0.48, 0.68, 0.55], dtype=np.float32)
    V = V / np.linalg.norm(V)
    H = (L + V) / np.linalg.norm(L + V)

    diff = np.abs(normals @ L)
    spec = np.clip(np.abs(normals @ H), 0.0, 1.0) ** 26.0
    rim = np.clip(1.0 - np.abs(normals @ V), 0.0, 1.0) ** 2.8 * np.clip(normals @ R_dir, 0.0, 1.0)

    base = np.array(base_rgb, dtype=np.float32)
    crimson_rim = np.array([1.0, 0.10, 0.50], dtype=np.float32)

    rgb = (0.32 + 0.64 * diff[:, None]) * base[None, :] + 0.35 * spec[:, None] + 0.22 * rim[:, None] * crimson_rim[None, :]
    rgb = np.clip(rgb, 0.0, 1.0)
    alpha = np.full((len(triangles), 1), 0.98, dtype=np.float32)
    return np.concatenate([rgb, alpha], axis=1)

def style_3d_axes(ax, mins, maxs, aspect, elev, azim, title, pad=12.0):
    ax.set_xlim(mins[0] - pad, maxs[0] + pad)
    ax.set_ylim(mins[1] - pad, maxs[1] + pad)
    ax.set_zlim(mins[2] - pad, maxs[2] + pad)
    ax.set_box_aspect(aspect)
    ax.view_init(elev=elev, azim=azim)
    ax.set_facecolor('#070409')
    ax.xaxis.pane.set_facecolor((0.07, 0.03, 0.08, 0.95))
    ax.yaxis.pane.set_facecolor((0.07, 0.03, 0.08, 0.95))
    ax.zaxis.pane.set_facecolor((0.05, 0.02, 0.06, 0.98))
    ax.xaxis.pane.set_edgecolor('#381232')
    ax.yaxis.pane.set_edgecolor('#381232')
    ax.zaxis.pane.set_edgecolor('#381232')
    ax.tick_params(colors='#b896b2', labelsize=6.5)
    ax.set_title(title, color='#f8f0f6', fontsize=7.8, fontweight='bold', pad=6)

def render_ieee_ras_blueprint(parts_dict, assy_tris, assy_groups, output_dirs):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(23, 12.5), dpi=175)
    fig.patch.set_facecolor('#050207')
    gs = GridSpec(2, 4, figure=fig, width_ratios=[1.25, 1.0, 1.0, 1.0], wspace=0.22, hspace=0.24)

    fig.suptitle(
        "IEEE RAS × E-JUST FLAGSHIP HUMANOID — 'AURA-EJUST v3.0' VIP RECEPTION ANDROID",
        fontsize=15.5, fontweight='bold', color='#ff1f4b', y=0.975
    )
    fig.text(
        0.5, 0.942,
        "AUTOMOTIVE SUPERCAR ROVER BASE | 4 FLARING WHEEL ARCHES | SEGMENTED BIONIC SPINE | 6.7\" PHONE KIOSK | 5-FINGER WELCOMING ARMS",
        ha='center', fontsize=9.0, color='#d8b4d2', fontweight='bold'
    )

    logo_badge_path = r"C:\Users\Lenovo\.gemini\antigravity\brain\0db2a8a2-1a68-47d9-bb42-3f66ca0441b3\.user_uploaded\media_1792236143258_1cfef822.png"
    if os.path.exists(logo_badge_path):
        logo_img = plt.imread(logo_badge_path)
        for x_pos in [0.025, 0.925]:
            ax_logo = fig.add_axes([x_pos, 0.915, 0.052, 0.072])
            ax_logo.imshow(logo_img)
            ax_logo.axis('off')

    # Panel 1 (Tall Left spanning 2 rows): Full Assembled Robot matching IEEE_RAS_EJUST_Humanoid_Showcase.jpg
    ax1 = fig.add_subplot(gs[:, 0], projection='3d')
    combined_t = []
    combined_c = []
    for g_tris, g_rgb in assy_groups:
        combined_t.append(g_tris)
        combined_c.append(compute_phong_colors(g_tris, g_rgb))
    all_t = np.concatenate(combined_t, axis=0)
    all_c = np.concatenate(combined_c, axis=0)
    poly_assy = Poly3DCollection(all_t, facecolors=all_c, edgecolors=(1.0, 0.12, 0.45, 0.08), linewidths=0.04)
    ax1.add_collection3d(poly_assy)
    pts = all_t.reshape(-1, 3)
    style_3d_axes(
        ax1, pts.min(axis=0), pts.max(axis=0),
        aspect=(1, 1, 1.85), elev=16, azim=48,
        title="06_Full_IEEE_RAS_Humanoid_Assembly.stl\nAURA-EJUST v3.0 (Photorealistic Concept Automotive Match)",
        pad=18.0
    )
    ax1.set_xlabel("X Width (mm)", color='#ff4d6d', fontsize=8)
    ax1.set_ylabel("Y Depth (mm)", color='#ff4d6d', fontsize=8)
    ax1.set_zlabel("Z Height (mm)", color='#ff4d6d', fontsize=8)

    # Panels 2..7: Individual Printable Parts with Authentic IEEE RAS x E-JUST Finishes
    configs = [
        ((0, 1), "01_Drive_Base_Chassis.stl (216 x 216 x 66 mm)\n4 Flared Arches + 2x JGA25, 2x Spine, 3S Bat, L298N, 2x Buck, 5-Ch IR",
         parts_dict['01'], (0.92, 0.94, 0.97), (1.0, 0.15, 0.35, 0.25), (1, 1, 0.36), 26, 38),
        ((0, 2), "02_Torso_NFC_Badge_Dock.stl (196 x 106 x 180 mm)\nAthletic V-Taper + 166x82mm Phone Dock + NFC Halo + ESP32",
         parts_dict['02'], (0.94, 0.95, 0.98), (1.0, 0.15, 0.45, 0.22), (1.12, 0.78, 1.05), 18, 34),
        ((0, 3), "03_Humanoid_Head_Shell.stl (172 x 136 x 142 mm)\nCyber-Visor Helmet + Dual Eye Bezels + Ear Turbines + Crest Fin",
         parts_dict['03'], (0.93, 0.94, 0.97), (1.0, 0.12, 0.45, 0.25), (1.15, 1.0, 0.98), 16, 36),
        ((1, 1), "04_Shoulder_Arm_Bracket.stl (132 x 68 x 56 mm)\nPauldron Dome Armor + MG996R Servo Cradle + Spine Clamp",
         parts_dict['04'], (0.46, 0.12, 0.54), (1.0, 0.15, 0.50, 0.25), (1.35, 0.85, 0.65), 28, 40),
        ((1, 2), "05_Spine_Aero_Fairing_Ring.stl (148 x 100 x 36 mm)\nToroidal Bionic Vertebra Rib + Dual Spine + Cooling Gills",
         parts_dict['05'], (0.75, 0.08, 0.28), (1.0, 0.20, 0.60, 0.25), (1.25, 0.90, 0.42), 26, 42),
        ((1, 3), "07_TFT_35_Adapter_Bezel.stl (165 x 81 x 9 mm)\nDrop-In Adapter (166x82mm Phone Dock -> 3.5\" SPI TFT)",
         parts_dict['07'], (0.18, 0.18, 0.24), (0.0, 0.90, 1.00, 0.28), (1.45, 0.75, 0.22), 34, 45),
    ]

    for (row, col), title, tris, base_rgb, edge_col, asp, elev, azim in configs:
        ax = fig.add_subplot(gs[row, col], projection='3d')
        colors = compute_phong_colors(tris, base_rgb)
        poly = Poly3DCollection(tris, facecolors=colors, edgecolors=edge_col, linewidths=0.08)
        ax.add_collection3d(poly)
        pts = tris.reshape(-1, 3)
        style_3d_axes(ax, pts.min(axis=0), pts.max(axis=0), aspect=asp, elev=elev, azim=azim, title=title)

    for out_dir in output_dirs:
        os.makedirs(out_dir, exist_ok=True)
        out_png = os.path.join(out_dir, "VIP_Humanoid_CAD_Blueprint.png")
        fig.savefig(out_png, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
        print(f"Saved Blueprint: {out_png}")
    plt.close(fig)

# ==============================================================================
# MAIN EXECUTION ROUTINE
# ==============================================================================

def main():
    print("=" * 78)
    print("IEEE RAS x E-JUST FLAGSHIP EDITION — 'AURA-EJUST v3.0' CAD & STL GENERATOR")
    print("=" * 78)

    stl_dir = r"C:\VIP_Humanoid_Robot\STL_3D_Print_Files"
    blueprint_dirs = [
        r"C:\VIP_Humanoid_Robot\CAD\Blueprints",
        r"C:\Users\Lenovo\.gemini\antigravity\brain\0db2a8a2-1a68-47d9-bb42-3f66ca0441b3",
    ]

    print("\n[1/7] Generating 01_Drive_Base_Chassis.stl ...")
    p01 = generate_part_01_aero_drive_base()
    write_binary_stl(os.path.join(stl_dir, "01_Drive_Base_Chassis.stl"), p01, "01_Drive_Base_Chassis")
    print(f"      -> {len(p01):6d} triangles | {p01.max(axis=(0,1)) - p01.min(axis=(0,1))} mm")

    print("\n[2/7] Generating 02_Torso_NFC_Badge_Dock.stl ...")
    p02 = generate_part_02_sculpted_torso_nfc(include_emblems=True)
    write_binary_stl(os.path.join(stl_dir, "02_Torso_NFC_Badge_Dock.stl"), p02, "02_Torso_NFC_Badge_Dock")
    print(f"      -> {len(p02):6d} triangles | {p02.max(axis=(0,1)) - p02.min(axis=(0,1))} mm")

    print("\n[3/7] Generating 03_Humanoid_Head_Shell.stl ...")
    p03 = generate_part_03_bionic_head_visor(include_emblem=True)
    write_binary_stl(os.path.join(stl_dir, "03_Humanoid_Head_Shell.stl"), p03, "03_Humanoid_Head_Shell")
    print(f"      -> {len(p03):6d} triangles | {p03.max(axis=(0,1)) - p03.min(axis=(0,1))} mm")

    print("\n[4/7] Generating 04_Shoulder_Arm_Bracket.stl ...")
    p04 = generate_part_04_bionic_shoulder()
    write_binary_stl(os.path.join(stl_dir, "04_Shoulder_Arm_Bracket.stl"), p04, "04_Shoulder_Arm_Bracket")
    print(f"      -> {len(p04):6d} triangles | {p04.max(axis=(0,1)) - p04.min(axis=(0,1))} mm")

    print("\n[5/7] Generating 05_Spine_Aero_Fairing_Ring.stl ...")
    p05 = generate_part_05_spine_fairing_ring()
    write_binary_stl(os.path.join(stl_dir, "05_Spine_Aero_Fairing_Ring.stl"), p05, "05_Spine_Aero_Fairing_Ring")
    print(f"      -> {len(p05):6d} triangles | {p05.max(axis=(0,1)) - p05.min(axis=(0,1))} mm")

    print("\n[6/7] Generating 07_TFT_35_Adapter_Bezel.stl ...")
    p07 = generate_part_07_tft35_adapter_bezel()
    write_binary_stl(os.path.join(stl_dir, "07_TFT_35_Adapter_Bezel.stl"), p07, "07_TFT_35_Adapter_Bezel")
    print(f"      -> {len(p07):6d} triangles | {p07.max(axis=(0,1)) - p07.min(axis=(0,1))} mm")

    print("\n[7/7] Generating 06_Full_IEEE_RAS_Humanoid_Assembly.stl & Phong-Shaded Blueprints ...")
    assy_tris, assy_groups = generate_part_06_full_assembly_colored(p01, p02, p03, p04, p05)
    write_binary_stl(os.path.join(stl_dir, "06_Full_IEEE_RAS_Humanoid_Assembly.stl"), assy_tris, "06_Full_Humanoid_Assy")
    print(f"      -> {len(assy_tris):6d} triangles | {assy_tris.max(axis=(0,1)) - assy_tris.min(axis=(0,1))} mm")

    parts_dict = {
        '01': p01, '02': p02, '03': p03,
        '04': p04, '05': p05, '07': p07,
    }

    print("\nRendering High-Resolution Phong-Shaded CAD Blueprint ...")
    render_ieee_ras_blueprint(parts_dict, assy_tris, assy_groups, blueprint_dirs)
    print("\nAll 3D STL print files and CAD blueprints generated successfully!")

if __name__ == "__main__":
    main()
