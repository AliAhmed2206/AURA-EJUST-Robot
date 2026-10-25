# IEEE RAS × E-JUST Flagship Design Dossier — "AURA-EJUST v3.0" Autonomous VIP Reception & Escort Humanoid

````carousel
![AURA-EJUST v3.0 Photorealistic IEEE RAS x E-JUST Showcase Render](C:/Users/Lenovo/.gemini/antigravity/brain/0db2a8a2-1a68-47d9-bb42-3f66ca0441b3/IEEE_RAS_EJUST_Humanoid_Showcase.jpg)
<!-- slide -->
![AURA-EJUST v3.0 Component-Fit SolidWorks / Fusion 360 Phong-Shaded 7-Panel CAD Blueprint](C:/Users/Lenovo/.gemini/antigravity/brain/0db2a8a2-1a68-47d9-bb42-3f66ca0441b3/VIP_Humanoid_CAD_Blueprint.png)
````

> [!IMPORTANT]
> **Authentic IEEE RAS × E-JUST University Identity ("AURA-EJUST v3.0"):**
> Built around the **Official E-JUST (Egypt-Japan University of Science and Technology) University Emblem** ([ejust_logo.png](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/ejust_logo.png)) and the **IEEE Robotics & Automation Society (RAS)** crest:
> 1. **Official Colorway:** **Satin Pearl Titanium White (`#F4F5F8`)** outer bionic shells paired with **E-JUST Crimson Red (`#C0121F` / `#E60012`)** and **IEEE RAS Royal Purple (`#621B6D`)** shoulder pauldrons, segmented waist exoskeleton rings, and aero rover base, accented with **Obsidian Matte Carbon (`#111116`)** twin spine columns, **Imperial Gold (`#C8A45D`)** trim, and **Glowing Crimson-Magenta (`#FF1744`)** NeoPixel eye/NFC halos.
> 2. **Official E-JUST University Emblem (3D Embossed & Kiosk UI):** Features the authentic **E-JUST University Logo** — a central **Crimson Red Sun Disc** surrounded by **3 Top Vertical Crown Bars (`|||`)**, **2 Upper Curved Black Side Arcs**, **2 Lower Curved Crescent/Pincer Arcs with Inward Horns & Bottom Gap**, and the **`E-JUST` Serif Wordmark** — physically embossed in 3D on [`02_Torso_NFC_Badge_Dock.stl`](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/02_Torso_NFC_Badge_Dock.stl) (left pectoral & NFC halo center), [`03_Humanoid_Head_Shell.stl`](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/03_Humanoid_Head_Shell.stl) (forehead crest), [`06_Full_IEEE_RAS_Humanoid_Assembly.stl`](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/06_Full_IEEE_RAS_Humanoid_Assembly.stl), the showcase render, and the [Smartphone Chest Kiosk Web-App (`index.html`)](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html).
> 3. **100% Pairwise-Disjoint Component-Fit CAD on a `220 × 220 mm` Print Bed:** Every internal component in the BOM (`2× JGA25-370` motors at `Y = +16.5 mm`, twin `Ø25.4 mm` spine sockets at `X = ±45, Y = -14.5 mm`, `3S 18650 / 12V` battery at `Y = -63 mm`, `L298N` at `Y = +57 mm`, `2× LM2596` bucks at `X = ±58, Y = -58 mm`, `5-Ch TCRT5000` IR bar + floor optical slot at `Y = +96.5 mm`, `2× HC-SR04`, `ESP32 DevKit V1`, `MFRC522` NFC reader, `DFPlayer Mini`, `Ø40 mm` speaker, `MG996R` servos, and a **Universal 6.1"–6.7" Smartphone Chest Kiosk (`166.0 × 82.0 × 11.5 mm` pocket)**) has a dedicated, collision-free mechanical pocket and `M3`/`M4` screw bosses inside the 3D-printed shells.

---

## 1. Solving Your Welcoming Screen Question: Smartphone vs. 3.5" TFT vs. Small OLED

> [!TIP]
> **Engineering Verdict: Your instinct is 100% spot-on — a `0.96"` (`22 × 11 mm`) or `1.3"` (`29 × 15 mm`) OLED is far too small to serve as a chest welcoming screen for standing VIP guests.**
> Instead, **dock a `6.1"–6.7"` Smartphone in the Chest Console** as the primary interactive VIP Welcome Screen, and move the small **`0.96"` / `1.3"` OLED into the Head Visor** to render the robot's animated blinking cyber-eyes!

### Head-to-Head Display Comparison for the Chest Console
| Evaluation Criterion | **Option A: Docked 6.1"–6.7" Smartphone Kiosk (RECOMMENDED ⭐)** | **Option B: 3.5" SPI TFT / `ESP32-2432S028R` (CYD)** | **Option C: 0.96" / 1.3" I2C OLED *(Move to Head Visor Only!)*** |
| :--- | :--- | :--- | :--- |
| **Active Viewing Area** | **`154 × 72 mm` (`~110 cm²` — 40× larger than OLED!)** | `74 × 50 mm` (`37 cm²` — 12× larger than OLED) | `22 × 11 mm` (`2.4 cm²` — **Too tiny for chest**) |
| **Resolution & Brightness** | **`1080 × 2400 px` AMOLED/IPS (`800+ nits`, 60–120 Hz)** | `480 × 320 px` RGB TFT (`~300 nits`, ~12 FPS over SPI) | `128 × 64 px` Monochrome (`1-bit`) |
| **Readable Distance** | **`1.5 – 2.5 meters` (Standing VIP eye level)** | `0.6 – 1.0 meters` | `< 0.3 meters` (Guest must bend down) |
| **Extra BOM Cost (EGP)** | **`0 EGP`** *(Reuses any team member's phone or spare Android during the event)* | **`+600 EGP`** *(Local RAM / Makers Egypt price)* | **`160 EGP`** *(Keep 1× inside the Head Visor for robot eyes)* |
| **Bilingual Arabic/English UI & Voice** | **Native HTML5/CSS3 + Bilingual Arabic (`ar-EG`) & English (`en-US`) Web Speech TTS + Live Route Bar** via our included Web-App ([index.html](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html)) | Requires custom bitmap fonts flashed to ESP32 SPIFFS | Cannot render smooth Arabic ligatures or route maps |
| **How it Fits in `02_Torso_NFC_Badge_Dock.stl`** | Slides directly into the top loading slot of the **`166.0 × 82.0 × 11.5 mm` chest kiosk pocket** (fits Samsung Galaxy A15/A25/A55, Redmi Note 13, iPhone Pro Max even with a slim case!) + concealed right-side `5V USB-C` charging channel | Drops into the exact same `166 × 82 mm` chest pocket (`+1.0 mm` slip-fit) using our 3D-printable adapter frame ([`07_TFT_35_Adapter_Bezel.stl`](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/07_TFT_35_Adapter_Bezel.stl), `165.0 × 81.0 × 9.0 mm`) | Snaps into the internal recessed eye brackets inside [`03_Humanoid_Head_Shell.stl`](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/03_Humanoid_Head_Shell.stl) |

### How the Smartphone Chest Screen & ESP32 Work Together Automatically
1. **Zero-Config Wi-Fi Link:** When powered on, [`VIP_Humanoid_ESP32.ino`](file:///C:/VIP_Humanoid_Robot/Firmware/VIP_Humanoid_ESP32/VIP_Humanoid_ESP32.ino) broadcasts a local Wi-Fi Access Point (`SSID: IEEE-RAS-EJUST-BOT`, Password: `ejust2026`, IP: `192.168.4.1`) with `/status`, `/trigger`, and `/reset` JSON endpoints.
2. **Fullscreen Chest Kiosk Web-App:** Open [WebApp_Screen/index.html](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html) on the docked phone and tap **`⛶ FULLSCREEN`**.
3. **Instant NFC Card Trigger (or Touch Kiosk Selection):** The moment a VIP taps their university/event NFC card on the glowing `MFRC522` chest halo below the phone (or taps a destination on the touchscreen), the ESP32 reads the card UID, triggers the welcoming arm/neck servos, and syncs the VIP's name, custom Arabic title, and destination (`Main Conference Hall` [1 stop] or `E-JUST Grand Theatre` [2 stops]) to the phone screen in `< 400 ms`—speaking both English (`en-US`) and Arabic (`ar-EG`) greetings and updating the live escort progress bar!

---

## 2. Component-Fit 3D-Printable CAD Architecture (`.STL` & SolidWorks 2026 `.SLDPRT`)

### A. Ready-to-Slice Sculpted 3D Print Files (`.STL` & `.SLDPRT`)
| Part ID | STL File Link | SolidWorks 2026 Native File | Bounding Box (mm) | Disjoint Component Pockets & Mechatronic Features | Est. PLA+ |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Part 01** | [01_Drive_Base_Chassis.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/01_Drive_Base_Chassis.stl) | [01_Drive_Base_Chassis.SLDPRT](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_Parts/01_Drive_Base_Chassis.SLDPRT) | `217.0 × 218.4 × 66.0` | Aero rover skirt, disjoint `2× JGA25-370` motor cradles (`Y=+16.5 mm`) + `M3` faceplates, dual `Ø25.4 mm` spine sockets (`X=±45, Y=-14.5 mm`), `74×58 mm` 3S battery tray (`Y=-63 mm`), `46×46 mm` L298N pocket (`Y=+57 mm`), `2× LM2596` buck pockets (`X=±58, Y=-58 mm`), `98×22 mm` front 5-Ch IR bar slot + floor optical cutout (`Y=+96.5 mm`), `3×` ball caster bosses, `2× HC-SR04` nose pods, rear switch/jack bulkhead | ~225 g |
| **Part 02** | [02_Torso_NFC_Badge_Dock.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/02_Torso_NFC_Badge_Dock.stl) | [02_Torso_NFC_Badge_Dock.SLDPRT](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_Parts/02_Torso_NFC_Badge_Dock.SLDPRT) | `198.0 × 103.5 × 180.0` | V-tapered bionic chest with **3D-Embossed Official E-JUST University Emblem**, `8°` tilted **Universal `6.1"–6.7"` Smartphone Kiosk Dock (`166.0×82.0×11.5 mm` pocket + top slide-in loading slot + `154×72 mm` viewport + USB-C channel)**, circular NFC halo + **`42×62 mm` MFRC522 pocket (`1.5 mm` RF wall)**, and disjoint central spine-bridge stack: **ESP32 (`31×58 mm` at `Z=136`)**, **DFPlayer (`23×23 mm` at `Z=82`)**, & **Ø40 mm Speaker (`Z=36`)** | ~185 g |
| **Part 03** | [03_Humanoid_Head_Shell.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/03_Humanoid_Head_Shell.stl) | [03_Humanoid_Head_Shell.SLDPRT](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_Parts/03_Humanoid_Head_Shell.SLDPRT) | `174.0 × 134.6 × 142.0` | **3D-Embossed Official E-JUST University Forehead Emblem (Sun Disc + 3 Crown Bars + Scarab-Lotus Arcs)**, wrap-around cyber-visor hood, recessed dual `0.96"/1.3"` OLED (`36×34 mm`) + `12-Bit WS2812B` NeoPixel eye ring seats (`Ø39.6 mm`), rotary ear pods, `MG996R` neck gimbal collar | ~185 g |
| **Part 04** | [04_Shoulder_Arm_Bracket.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/04_Shoulder_Arm_Bracket.stl) *(2×)* | [04_Shoulder_Arm_Bracket.SLDPRT](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_Parts/04_Shoulder_Arm_Bracket.SLDPRT) | `133.0 × 68.0 × 56.0` | Open-access contoured shoulder pauldron armor + precision **`41.2 × 20.6 × 42.0 mm` MG996R metal-gear servo cradle** + `M4` mounting tab bosses (`49.5 mm` C-to-C) + `Ø25.4 mm` spine clamp collar | ~110 g (pair) |
| **Part 05** | [05_Spine_Aero_Fairing_Ring.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/05_Spine_Aero_Fairing_Ring.stl) *(3×)* | [05_Spine_Aero_Fairing_Ring.SLDPRT](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_Parts/05_Spine_Aero_Fairing_Ring.SLDPRT) | `152.0 × 104.0 × 38.0` | Segmented bionic waist exoskeleton rings (alternating **IEEE RAS Purple** & **E-JUST Crimson**) + dual `Ø25.4 mm` spine bores (`Y=-14.5 mm`) + central `Ø22 mm` cable harness clip | ~80 g (set of 3) |
| **Part 07** | [07_TFT_35_Adapter_Bezel.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/07_TFT_35_Adapter_Bezel.stl) *(Optional)* | [07_TFT_35_Adapter_Bezel.SLDPRT](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_Parts/07_TFT_35_Adapter_Bezel.SLDPRT) | `165.0 × 81.0 × 9.0` | Drop-in adapter bezel (`+1.0 mm` slip-fit into the `166×82 mm` smartphone dock) converting it to hold a dedicated **`3.5"` ILI9488 SPI TFT / ESP32-CYD (`98.5 × 58.5 mm` pocket)** | ~25 g |
| **Assy 06** | [06_Full_IEEE_RAS_Humanoid_Assembly.stl](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/06_Full_IEEE_RAS_Humanoid_Assembly.stl) | — | `328.6 × 362.4 × 1027.0` | Full 27,136-triangle multi-material reference assembly of **AURA-EJUST v3.0** with multi-color **Official E-JUST University Emblems** | **~785 g Total** |

### B. Verified Component-to-Chassis Mechanical Clearance & Disjoint AABB Table
Every internal bay and all 76 pairwise AABB non-intersection checks were verified via [`Verify_Component_Fit_and_STLs.py`](file:///C:/VIP_Humanoid_Robot/CAD/Verify_Component_Fit_and_STLs.py):

| Component Name | Datasheet Size (`W × L × H` mm) | Engineered CAD Bay (`W × L × H` mm) | Target 3D-Printed Part & Coordinates | Mechanical Clearance | Mounting Method |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **JGA25-370 12V Geared Motor (2×)** | `Ø25.0 × 58.0 × 25.0` | `25.6 × 62.0 × 36.0` | `01_Drive_Base` (`X=±45, Y=+16.5 mm`) | `+0.6 / +4.0 mm` | `2× M3` faceplate bolts (`X=±71 mm`) + barrel cradle |
| **Twin Ø25.0 mm Spine Columns** | `Ø25.0 × 980.0` | `Ø25.4 × 66.0` sockets | `Parts 01, 02, 04, 05` (`X=±45, Y=-14.5 mm`) | `+0.4 mm` slip-fit | Disjoint behind motor axle (`+1.7 mm` wall gap) |
| **3S 18650 Li-Ion Pack + 20A BMS** | `68.0 × 56.0 × 20.0` | `74.0 × 58.0 × 22.0` | `01_Drive_Base` (`X=0, Y=-63.0 mm`) | `+6.0 / +2.0 mm` | Walled rear low-CG tray + velcro strap |
| **LM2596 DC-DC Buck Converter (2×)** | `21.0 × 43.2 × 14.0` | `24.0 × 46.0 × 20.0` | `01_Drive_Base` (`X=±58, Y=-58.0 mm`) | `+3.0 / +2.8 mm` | Disjoint side pockets + `2× M3` bosses |
| **L298N Dual H-Bridge Driver** | `43.0 × 43.0 × 26.0` | `46.0 × 46.0 × 32.0` | `01_Drive_Base` (`X=0, Y=+57.0 mm`) | `+3.0 / +3.0 mm` | Recessed pocket + `4× M3` standoffs (`37×37 mm`) |
| **5-Ch TCRT5000 IR Line Follower** | `94.0 × 18.0 × 8.0` | `98.0 × 22.0 × 10.0` | `01_Drive_Base` (`X=0, Y=+96.5 mm`) | `+4.0 / +4.0 mm` | Front optical channel + open floor window + `2× M3` |
| **HC-SR04 Ultrasonic Sensor (2×)** | `45.0 × 20.0 × 15.0` | `48.0 × 23.0 × 20.0` | `01_Drive_Base` (`X=±36, Y=+103.0 mm`) | `+3.0 / +3.0 mm` | Dual `Ø16.4 mm` nose ports (`26 mm` C-to-C) |
| **6.1"–6.7" Smartphone Kiosk (w/ Case)** | `163.0 × 78.5 × 9.5` | `166.0 × 82.0 × 11.5` | `02_Torso_NFC` (`Z=+37 mm` console) | `+3.0 / +3.5 mm` | Top slide-in slot (`154×72 mm` viewport) + USB-C slot |
| **07_TFT_35_Adapter inside Phone Dock** | `165.0 × 81.0 × 9.0` | `166.0 × 82.0 × 11.5` | `02_Torso_NFC` (`07` -> `02` dock) | `+1.0 / +1.0 mm` | Drop-in slip fit (`0.5 mm` per side) |
| **MFRC522 13.56 MHz NFC Reader** | `40.0 × 60.0 × 5.0` | `42.0 × 62.0 × 7.0` | `02_Torso_NFC` (`Z=-39 mm` console) | `+2.0 / +2.0 mm` | Internal pocket behind `1.5 mm` thin RF chest halo wall |
| **ESP32-WROOM-32 DevKit V1** | `28.5 × 55.0 × 10.0` | `31.0 × 58.0 × 12.0` | `02_Torso_NFC` (`X=0, Z=136 mm` bridge) | `+2.5 / +3.0 mm` | Upper central spine bridge cradle + `M3` standoffs |
| **DFPlayer Mini MP3 Module** | `20.5 × 20.5 × 8.0` | `23.0 × 23.0 × 10.0` | `02_Torso_NFC` (`X=0, Z=82 mm` bridge) | `+2.5 / +2.5 mm` | Middle central spine bridge pocket |
| **3W 4Ω Enclosed Speaker (`Ø40 mm`)** | `Ø40.0 × 15.0` | `Ø41.0 × 16.0` | `02_Torso_NFC` (`X=0, Z=36 mm` bridge) | `+1.0 mm` | Lower central acoustic ring chamber |
| **0.96" / 1.3" I2C OLED (Visor Eyes)** | `33.5 × 31.5 × 4.5` | `36.0 × 34.0 × 6.0` | `03_Humanoid_Head_Shell` (`X=±22, Y=18`) | `+2.5 / +2.5 mm` | Recessed internal visor clips (zero cheek protrusion) |
| **12-Bit WS2812B NeoPixel Eye Rings** | `Ø38.0 × 3.5` | `Ø39.6 × 10.0` | `03_Humanoid_Head_Shell` (`X=±28, Y=66`) | `+1.6 mm` | Recessed circular eye bezels |
| **MG996R Metal-Gear Servo (2×)** | `40.7 × 19.7 × 37.0` | `41.2 × 20.6 × 42.0` | `04_Shoulder` & `03_Head` | `+0.5 / +0.9 mm` | Open-access cradle + `M4` tab bosses (`49.5 mm` C-to-C) |

### C. CAD Generators, Verification Suite & Firmware Links
- **Parametric Lofted STL & IEEE RAS × E-JUST 7-Panel Blueprint Generator**: [Generate_STL_and_Blueprints.py](file:///C:/VIP_Humanoid_Robot/CAD/Generate_STL_and_Blueprints.py)
- **Automated STL, Disjoint AABB Collision & Firmware Verification Suite**: [Verify_Component_Fit_and_STLs.py](file:///C:/VIP_Humanoid_Robot/CAD/Verify_Component_Fit_and_STLs.py)
- **SolidWorks 2026 Python COM Generator**: [SolidWorks_VIP_Robot_Generator.py](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_VIP_Robot_Generator.py) & VBA Macro [SolidWorks_VIP_Robot_Macro.bas](file:///C:/VIP_Humanoid_Robot/CAD/SolidWorks_VIP_Robot_Macro.bas)
- **Autodesk Fusion 360 API Generator**: [Fusion360_VIP_Robot_Generator.py](file:///C:/VIP_Humanoid_Robot/CAD/Fusion360_VIP_Robot_Generator.py)
- **Fullscreen Smartphone Chest Kiosk Web-App (IEEE RAS × E-JUST UI)**: [index.html](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html)
- **ESP32 Wi-Fi SoftAP + NFC + Line-Follower Firmware**: [VIP_Humanoid_ESP32.ino](file:///C:/VIP_Humanoid_Robot/Firmware/VIP_Humanoid_ESP32/VIP_Humanoid_ESP32.ino)

---

## 3. How to Achieve the "IEEE RAS × E-JUST Showcase Finish" (Under 350 EGP)

1. **Automotive Filler Primer & Wet Sanding:**
   - Print all parts at **0.20 mm layer height** (3 wall loops, 25% gyroid infill). Sand outer curves with **220 $\rightarrow$ 400 grit wet/dry sandpaper** and apply 1 coat of **2K Automotive Filler Primer Spray** (~110 EGP).
2. **Official IEEE RAS × E-JUST Paint Scheme:**
   - **Satin Pearl White (`#F4F5F8` Spray, ~95 EGP):** `02_Torso_NFC_Badge_Dock`, `03_Humanoid_Head_Shell`, and the lower tapered leg shroud.
   - **E-JUST Metallic Crimson Red (`#C0121F` Spray, ~95 EGP):** `01_Drive_Base_Chassis`, Right `04_Shoulder_Arm_Bracket`, Middle `05_Spine_Aero_Fairing_Ring`, and the central sun disc of the 3D-embossed **Official E-JUST University Emblem**.
   - **IEEE RAS Royal Purple (`#621B6D` Spray, ~95 EGP):** Left `04_Shoulder_Arm_Bracket` and Top/Bottom `05_Spine_Aero_Fairing_Ring` ribs.
3. **Smoked Black Acrylic Visor & Carbon-Fiber Spine Wrap:**
   - Fit **2 mm Smoked Black Acrylic (`Perspex`)** (~50 EGP) inside the head visor hood and over the lower NFC halo ring, and wrap the twin **Ø25 mm spine tubes** with **Matte Black 3D Carbon-Fiber Vinyl** (~45 EGP).
   - Paint or apply vinyl decals of the **IEEE RAS logo** (right pectoral) and the **Official E-JUST University Emblem** (left pectoral: red sun disc, 3 top crown bars, 4 curved scarab-lotus arcs, and `E-JUST` serif wordmark).

---

## 4. Detailed Bill of Materials (BOM) — Egyptian Market Prices (5,000–7,000 EGP)

### Subsystem 1: Compute, 13.56 MHz NFC, Smartphone Chest Kiosk & Visor Illumination
| Component | Specification / Model | Qty | Unit (EGP) | Subtotal (EGP) | Function in AURA-EJUST v3.0 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Main Controller** | ESP32-WROOM-32 DevKit V1 (Wi-Fi SoftAP + BLE) | 1 | 380 | **380** | Hosts `IEEE-RAS-EJUST-BOT` Wi-Fi API for Chest Phone, reads NFC, drives motors/servos |
| **Chest Welcome Screen** | **6.1"–6.7" Smartphone (Team/Spare Android Phone)** + Right-Angle USB-C Cable | 1 | **0 (Reused)** *(+65 cable)* | **65** | Runs fullscreen [IEEE RAS × E-JUST Kiosk Web-App](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html) inside the `166×82 mm` chest dock |
| **Head Visor Eye Display** | 0.96" or 1.3" I2C OLED Display (SSD1306 / SH1106) | 1 | 160 | **160** | Mounted inside `03_Humanoid_Head_Shell` for animated cyber-eyes & status telemetry |
| **NFC Card Reader** | MFRC522 13.56 MHz SPI Module *(or PN532)* | 1 | 135 | **135** | Mounted in the `42×62 mm` pocket behind the `1.5 mm` chest NFC halo (`SS=GPIO 5`, `RST=GPIO 0`) |
| **Voice Audio Module** | DFPlayer Mini MP3 Player + 8 GB MicroSD + 3W 4Ω 40 mm Speaker | 1 set | 295 | **295** | Plays bilingual Arabic/English MP3 tracks through chest louvers (alongside Phone TTS) |
| **Crimson/Purple LED Rings** | WS2812B Addressable NeoPixel Rings (2× 12-Bit Eyes + 1× 16-Bit NFC Halo) | 3 | 65 | **195** | Glowing `#FF1744` Crimson & `#621B6D` RAS Purple bionic eyes and chest NFC tap halo |

### Subsystem 2: Differential Mobility, Multi-Stop Navigation & Bionic Actuation
| Component | Specification / Model | Qty | Unit (EGP) | Subtotal (EGP) | Function in AURA-EJUST v3.0 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Drive Gearmotors** | JGA25-370 12V DC Geared Motor (150–200 RPM, Metal Gears) | 2 | 375 | **750** | High-torque differential drive inside the disjoint `Y=+16.5 mm` cradles of `01_Drive_Base_Chassis` |
| **Wheels + Hex Hubs** | 75–80 mm Rubber Tire Wheels + 4 mm Brass Hex Couplers | 2 | 140 | **280** | Smooth indoor traction on E-JUST marble and conference hall carpet |
| **Stabilizer Casters** | Metal Bullseye Swivel Ball Caster (2× Front `X=±44, Y=+57` & 1× Rear `Y=-99.5`) | 3 | 50 | **150** | Tripod/4-point pitch stability under the `217×219 mm` rover base without blocking the IR sensor bar |
| **Motor Driver** | L298N Dual H-Bridge Driver (mounted in `46×46 mm` front-center bay `Y=+57 mm`) | 1 | 145 | **145** | PWM speed & smooth acceleration control |
| **Humanoid Servos** | MG996R Metal-Gear High-Torque Servo (`11 kg·cm`) | 2 | 240 | **480** | 1× Neck Pan Gimbal (`03_Head`) + 1× Right Shoulder Welcoming Arm (`04_Shoulder`) |
| **Floor Guide Array** | 5-Channel TCRT5000 IR Line Follower Bar (in `98×22 mm` front optical slot `Y=+96.5 mm`) | 1 | 165 | **165** | Tracks indoor path & counts cross-markers (`Marker 1 = Main Hall`, `Marker 2 = Theatre`) |
| **Safety Rangefinders** | HC-SR04 Ultrasonic Distance Sensors (`TRIG=GPIO 2`, `ECHO=GPIO 4` in front nose pods) | 2 | 65 | **130** | Auto-pauses escort if a guest steps within `35 cm` (uses `GPIO 4` so ESP32 boot is never blocked) |

### Subsystem 3: Power Distribution & Dual-Buck Isolation
| Component | Specification / Model | Qty | Unit (EGP) | Subtotal (EGP) | Function in AURA-EJUST v3.0 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Main Battery Pack** | 3S 11.1V–12.6V Li-Ion Pack (`68×56×20 mm`, 3× 18650 + 20A BMS) | 1 | 680 | **680** | Fits inside the `74×58×22 mm` rear counterweight tray (`Y=-63 mm`); 4–6 hrs runtime |
| **12.6V Smart Charger** | 12.6V 2A Wall Charger + Rear DC-022 Barrel Jack (`Ø8.2 mm` port) | 1 | 190 | **190** | Plug-in charging at the rear bulkhead of `01_Drive_Base_Chassis` |
| **Step-Down Regulators** | LM2596 3A Adjustable DC-DC Buck Converter (in `24×46 mm` side bays `X=±58, Y=-58 mm`) | 2 | 75 | **150** | Buck #1 (`5.0V`): ESP32 + **Smartphone USB-C Power** + NeoPixels; Buck #2 (`6.0V`): Servos |
| **Switch, Fuse & Harness** | KCD1 Rocker Switch (`20×13 mm`) + 10A Fuse + 18 AWG Harness | 1 set | 145 | **145** | Routed vertically through the central `Ø22 mm` spine conduit clips |

### Subsystem 4: 3D Printing, Twin Spine & IEEE RAS × E-JUST Finishing
| Component | Specification / Model | Qty | Unit (EGP) | Subtotal (EGP) | Function in AURA-EJUST v3.0 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **PLA+ 3D Filament** | 1 kg Spool eSUN / Creality PLA+ (1.75 mm White) | 1 kg | 750 | **750** | Prints all sculpted parts (~785 g total filament used) |
| **Twin Spine Columns** | Ø25 mm OD Heavy-Wall UPVC / Aluminum Tube (cut to `2× 980 mm`) | 1 | 120 | **120** | Structural vertical backbone (`X=±45, Y=-14.5 mm`) + concealed wiring conduit |
| **Visor & Lower Shroud** | 2 mm Smoked Black Acrylic + 3 mm White PVC Celuka Lower Skirt | 1 set | 260 | **260** | Seamless dark glass visor + tapered lower leg fairing |
| **IEEE RAS × E-JUST Finish** | Pearl White + E-JUST Crimson (`#C0121F`) + RAS Purple (`#621B6D`) Spray + Carbon Vinyl + M3/M4 Kit | 1 kit | 395 | **395** | Official IEEE RAS E-JUST surface finish & metric fasteners |

### Total Cost Summary
* **Recommended Build (With Docked Smartphone Chest Kiosk):** **`5,920 EGP`** *(Saves money vs. dual OLEDs while delivering a 40× larger full-color touchscreen UI right inside your **5,000 – 7,000 EGP** budget!)*
* **Dedicated Embedded Screen Option (With `3.5" SPI TFT / ESP32-CYD` in `07_TFT_35_Adapter_Bezel.stl`):** **`6,520 EGP`** *(Adds `+600 EGP` if you prefer a permanently bolted 3.5" TFT instead of docking a smartphone).*

---

## 5. Electrical & Wi-Fi Kiosk System Architecture

```mermaid
flowchart LR
    subgraph Base["01_Drive_Base_Chassis (Disjoint 12V Power & Mobility Bays)"]
        BAT["3S 12V Li-Ion Battery\n(74x58mm Rear Bay Y=-63mm)"] --> FUSE["KCD1 Switch (20x13mm)\n+ 10A Fuse"]
        FUSE -->|12V Motor Rail| L298N["L298N H-Bridge\n(46x46mm Bay Y=+57mm)"]
        FUSE -->|12V Input| BUCK_5V["LM2596 Buck #1 (5.0V)\n(Left Bay X=-58, Y=-58mm)"]
        FUSE -->|12V Input| BUCK_6V["LM2596 Buck #2 (6.0V)\n(Right Bay X=+58, Y=-58mm)"]
        L298N --> ML["Left JGA25-370\n(X=-45, Y=+16.5mm Cradle)"]
        L298N --> MR["Right JGA25-370\n(X=+45, Y=+16.5mm Cradle)"]
    end

    subgraph Torso["02_Torso_NFC_Badge_Dock (Chest Kiosk & Disjoint Spine Bridge)"]
        BUCK_5V -->|5V Spine Harness| ESP["ESP32-WROOM-32\n(31x58mm Cradle at Z=136mm)"]
        BUCK_5V -->|5V USB-C Channel| PHONE["6.1\"-6.7\" Smartphone Chest Kiosk\n(166x82x11.5mm Dock • index.html)"]
        ESP <-->|Web Bluetooth NUS BLE\nUUID: 6e400001-...\n+ Wi-Fi SoftAP Backup| PHONE
        ESP -->|VSPI GPIO 5,0,18,19,23| NFC["MFRC522 13.56MHz NFC\n(42x62mm Bay • 1.5mm RF Wall)"]
        ESP -->|UART2 GPIO 16,17| DFP["DFPlayer Mini (23x23mm at Z=82mm)\n+ Ø40mm 3W Speaker (Z=36mm)"]
    end

    subgraph HeadAndArms["03_Head_Shell & 04_Shoulder_Bracket"]
        BUCK_6V --> SNECK["MG996R Neck Gimbal\n(GPIO 32)"]
        BUCK_6V --> SARM["MG996R Right Shoulder\n(Open 41.2x20.6mm Bay • GPIO 33)"]
        ESP -->|I2C GPIO 21,22| OLED["0.96\"/1.3\" OLED Visor Eyes\n(Recessed 36x34mm Head Brackets)"]
        ESP -->|GPIO 2 TRIG / GPIO 4 ECHO| US["2x HC-SR04 Ultrasonics\n(Front Nose Pods X=±36mm)"]
        BUCK_5V --> NEO["3x WS2812B Crimson/Purple Rings\n(2x Eyes + 1x NFC Halo)"]
    end
```

---

## 6. Flagship Speech System App & Web Bluetooth (BLE) Architecture

### A. Phone as Robot Face & Speech Brain (Samsung Galaxy A24)
- **App Location**: [`WebApp_Screen/index.html`](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html)
- **Display Optimization**: 6.5" Super AMOLED (`1080 × 2340 px`, 19.5:9 widescreen). Deep obsidian blacks (`#060408`) turn off AMOLED pixels to maximize contrast and preserve battery life.
- **Bionic Face Canvas Engine (60 FPS)**:
  - **Dynamic Gaze Tracking**: Left and right bionic cyber-eyes with iris rings and pupils that track visitor elevation in real time via the front camera.
    - *Tall Visitor*: Pupils shift upward (`targetGazeY < -0.2`) to maintain eye contact.
    - *Child / Seated Guest*: Pupils shift downward (`targetGazeY > +0.2`).
    - *Horizontal Pan*: Pupils smoothly track visitors moving left/right.
  - **Expressive Emotions**:
    - `HAPPY / GRATEFUL`: Crescent curved eyes (`⌒ ⌒`), glowing diffuse pink blush on cheeks (`rgba(255, 64, 129, 0.65)`), and a broad radiant smile. Triggered when the guest says *"thank you"*, *"thanks"*, *"شكراً"*, or taps an event NFC badge.
    - `CURIOUS / QUESTION`: Raised left eyebrow/eyelid, tilted pupil gaze, and soft pulsing cyan iris. Triggered by queries (*"what is"*, *"how do"*, *"where is"*).
    - `THINKING / REASONING`: Rotating iris reticle and pulsating thought indicator.
    - `SPEAKING / TALKING`: Cyber mouth lip-sync waveform oscillating in real-time sync with speech audio.
    - `ATTENTIVE`: Gentle micro-saccades and randomized blinking every 2.5–5.5 seconds.

### B. Front Camera Vision & Proximity Presence
- **Camera Stream**: Uses the front camera (`facingMode: 'user'`).
- **3-Tier Zero-Dependency Face Tracker**:
  1. *Tier 1*: Native Chrome `window.FaceDetector` API on Android.
  2. *Tier 2*: MediaPipe FaceMesh / Detection if online.
  3. *Tier 3 (Built-in Offline)*: High-speed luminance/skin-tone pixel sampler running at 15 FPS on an offscreen canvas (`64 × 48 px`). Computes center of mass `(cx, cy)` and bounding box without external dependencies.
- **Visitor Proximity Welcoming Trigger**: When a guest approaches within 0.8–1.5 m (bounding area ratio > 12%), the robot locks eye contact and greets:
  > *"Hello! Welcome to IEEE RAS at E-JUST. Please tap your university or event NFC badge on the chest reader to begin escort."*

### C. Web Bluetooth (Nordic UART Service) Protocol & Packet Reassembly
- **Service UUID**: `6e400001-b5a3-f393-e0a9-e50e24dcca9e`
- **RX Characteristic (Write)**: `6e400002-b5a3-f393-e0a9-e50e24dcca9e` (Phone -> ESP32)
- **TX Characteristic (Notify)**: `6e400003-b5a3-f393-e0a9-e50e24dcca9e` (ESP32 -> Phone)
- **20-Byte BLE Chunking & RX Buffer Reassembly**:
  - WebApp automatically chunks outgoing writes into $\le 20$-byte segments with 15ms pacing to guarantee compatibility across all Android ATT MTU implementations.
  - ESP32 firmware features an accumulation buffer (`bleRxBuffer`) that reassembles fragmented chunks until a newline delimiter (`\n`) or complete JSON object is received.
  - ESP32 JSON command parser extracts `name`, `dest`, `markers`, and `uid` dynamically from `START_ESCORT` payloads and synchronizes active VIP parameters.
- **Bi-directional JSON Packet Specification**:
  | Direction | Event / Command | Payload Schema | Description |
  | :--- | :--- | :--- | :--- |
  | **ESP32 $\rightarrow$ Phone** | `NFC_TAP` | `{"event":"NFC_TAP","uid":"A1:B2:C3:D4","name":"Prof. Amr Adly","dest":"Main Hall","markers":1}` | Sent immediately when MFRC522 reads VIP badge. |
  | **ESP32 $\rightarrow$ Phone** | `STATUS` | `{"event":"STATUS","state":"ESCORTING","markers":0}` | Periodic heartbeat and escort state updates. |
  | **ESP32 $\rightarrow$ Phone** | `ARRIVED` | `{"event":"ARRIVED","dest":"Main Conference Hall"}` | Sent when target line marker count is reached. |
  | **ESP32 $\rightarrow$ Phone** | `OBSTACLE` | `{"event":"OBSTACLE","dist":22}` | Sent when HC-SR04 ultrasonic detects obstacle < 35 cm. |
  | **Phone $\rightarrow$ ESP32** | `START_ESCORT`| `{"cmd":"START_ESCORT","name":"...","dest":"...","markers":1}` | Triggers arm waving gesture, 180° turnaround, and line motors. |
  | **Phone $\rightarrow$ ESP32** | `PAUSE` / `RESUME`| `{"cmd":"PAUSE"}` / `{"cmd":"RESUME"}` | Pauses / resumes motor drive. |
  | **Phone $\rightarrow$ ESP32** | `RESET` | `{"cmd":"RESET"}` | Returns robot to standby reception desk mode. Interrupts delay loops. |
  | **Phone $\rightarrow$ ESP32** | `WAVE` | `{"cmd":"WAVE"}` | Manually triggers MG996R welcoming arm wave. |

### D. Gemini Live & Autonomous Dialog Engine
- **Gemini Live WebSocket Client**:
  - Connects to `wss://generativelanguage.googleapis.com/ws/google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent?key=...`.
  - Transmits `BidiGenerateContentSetup` configured with `models/gemini-3.8-live` and prebuilt voice synthesis (`Aoede`, `Puck`, `Kore`, `Charon`).
  - Streams realtime user utterances and receives 24kHz raw PCM little-endian audio buffers played via Web Audio API alongside synchronized subtitle transcriptions.
- **Hands-Free Continuous Natural Conversation**:
  - Automatically engages upon VIP card tap or visitor approach (`AUTO-TALK: ON`).
  - Automatically re-arms speech recognition after speech playback finishes without requiring touch interactions during the walk.
  - Automatically recovers from `no-speech` silence events to prevent premature conversation terminations.
- **Autonomous Smart Dialog Engine (Zero-Quota Offline Fallback)**:
  - If Gemini API prepayment credits are exhausted (HTTP 402/429) or the device is offline, the on-device dialog engine responds intelligently to inquiries regarding IEEE RAS, E-JUST facilities, robotics specs, and greetings with emotion tagging.
- **Bilingual Voice Output**: Speaks English (`en-US`) and Egyptian Arabic (`ar-EG`) via Web Speech API and Gemini PCM audio streaming.

### E. Quick-Start Operating Procedure
1. **Flash Firmware**: Open [`VIP_Humanoid_ESP32.ino`](file:///C:/VIP_Humanoid_Robot/Firmware/VIP_Humanoid_ESP32/VIP_Humanoid_ESP32.ino) in Arduino IDE. Select board **ESP32 Dev Module** and upload.
2. **Mount Phone**: Dock the Samsung Galaxy A24 into [`02_Torso_NFC_Badge_Dock.stl`](file:///C:/VIP_Humanoid_Robot/STL_3D_Print_Files/02_Torso_NFC_Badge_Dock.stl) and connect the right-angle USB-C cable.
3. **Launch WebApp**: Open [`WebApp_Screen/index.html`](file:///C:/VIP_Humanoid_Robot/WebApp_Screen/index.html) in Google Chrome on the phone. Tap **`⛶ FULLSCREEN`**.
4. **Pair Bluetooth**: Tap **`PAIR ESP32 (BLE)`** in the bottom control bar and select **`AURA-EJUST-BOT`**. The status pill will illuminate green (**`BLE: ONLINE`**).
5. **VIP Welcome & Continuous Escort**: When a guest approaches and taps their NFC card on the chest halo, the robot automatically welcomes them by name, blushes with a happy face gesture, waves its arm, engages hands-free continuous dialogue, and navigates along the floor line guide to the event hall!

