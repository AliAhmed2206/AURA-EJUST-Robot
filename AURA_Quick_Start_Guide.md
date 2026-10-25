# AURA-EJUST: VIP Humanoid Robot — Quick Start & Bring-Up Guide

Welcome to the **AURA-EJUST VIP Humanoid Robot Project** created for the **IEEE RAS Student Branch at Egypt-Japan University of Science and Technology (E-JUST)**.

This repository contains the complete mechanical, electrical, firmware, and AI web-screen stack for the humanoid reception and escort robot.

---

## 1. Hardware Pinout & Wiring Diagram (ESP32 DevKit V1)

All pins are pre-configured in both firmware sketches. Connect your components as follows:

### A. L298N Dual H-Bridge Motor Driver (4 DC Motors)
| L298N Terminal / Pin | ESP32 DevKit V1 Pin | Function |
| :--- | :--- | :--- |
| **ENA** (Remove jumper) | **GPIO 25** | Left Motors PWM Speed Control (0–255) |
| **IN1** | **GPIO 26** | Left Motors Direction 1 |
| **IN2** | **GPIO 27** | Left Motors Direction 2 |
| **IN3** | **GPIO 14** | Right Motors Direction 1 |
| **IN4** | **GPIO 12** | Right Motors Direction 2 |
| **ENB** (Remove jumper) | **GPIO 13** | Right Motors PWM Speed Control (0–255) |
| **GND** | **GND** | **Common Ground** (Must tie to ESP32 GND!) |
| **+12V / VMS** | **Battery + (7.4V–12V)** | Motor Power Supply |
| **+5V (Logic Out)** | **VIN / 5V** | Optional power to ESP32 (if 12V jumper attached) |

> [!IMPORTANT]
> **Common Ground**: Always connect the battery ground, L298N ground, and ESP32 GND together. If grounds are not tied, motors will jitter or fail to respond.

---

### B. MFRC522 NFC Card Reader (Hardware VSPI)
| MFRC522 Pin | ESP32 DevKit V1 Pin | Color / Notes |
| :--- | :--- | :--- |
| **3.3V** | **3V3** | **NEVER connect to 5V! MFRC522 is 3.3V only** |
| **RST** | **GPIO 21** | Reset |
| **GND** | **GND** | Ground |
| **MISO** | **GPIO 19** | Master In Slave Out |
| **MOSI** | **GPIO 23** | Master Out Slave In |
| **SCK** | **GPIO 18** | SPI Clock |
| **SDA / SS** | **GPIO 5** | Chip Select |

---

### C. HC-SR04 Ultrasonic Collision Sensor
| HC-SR04 Pin | ESP32 DevKit V1 Pin | Notes |
| :--- | :--- | :--- |
| **VCC** | **5V / VIN** | 5V Power |
| **GND** | **GND** | Ground |
| **Trig** | **GPIO 2** | Trigger Output |
| **Echo** | **GPIO 4** | Echo Input (Use 1k/2k resistor voltage divider if needed) |

---

### D. TCRT5000 Ground IR Line Tracking Sensors
| Sensor Pin | ESP32 DevKit V1 Pin | Function |
| :--- | :--- | :--- |
| **Left IR D0** | **GPIO 34** | Left ground tracking sensor |
| **Right IR D0** | **GPIO 35** | Right ground tracking sensor (or `-1` if using 1 IR) |
| **VCC & GND** | **3V3 & GND** | Sensor power |

---

## 2. Firmware Options

You have two ready-to-flash Arduino sketches in the `Firmware/` folder:

### Option 1: Autonomous Reception & Web Screen Mode (Recommended)
📁 **`Firmware/VIP_Humanoid_ESP32/VIP_Humanoid_ESP32.ino`**
- **How it works**: Connects directly to the robot face web app over **Web Bluetooth (BLE Nordic UART)** without needing any phone app installation.
- **Features**:
  - Pre-loaded with all **21 VIP cards** (`53B80572420001` .. `53E00572420001`).
  - Automatically recognizes cards and greets guests (*"Welcome, VIP Guest X!"*).
  - **Full Voice Control**:
    - *"Move forward"* / *"امشي لقدام"* $\rightarrow$ Drives forward for 1.5s with obstacle protection.
    - *"Back up"* / *"ارجعي لورا"* $\rightarrow$ Reverses for 1.5s.
    - *"Turn right"* / *"حودي يمين"* $\rightarrow$ Spins right.
    - *"Turn left"* / *"حودي شمال"* $\rightarrow$ Spins left.
    - *"Stop moving"* / *"اقفي هنا"* $\rightarrow$ Hard brake.
    - *"Continue moving"* / *"يلا كملي"* $\rightarrow$ Resumes escort.
  - **Autonomous Line Following**: Ground IR sensors steer the wheels along black tape on the floor.
  - **Ultrasonic Safety Brake**: Stops motors in 20 ms if an obstacle appears closer than 35 cm.

### Option 2: Dabble Mobile GamePad Mode (Direct Smartphone RC)
📁 **`Firmware/AURA_Dabble_Gamepad/AURA_Dabble_Gamepad.ino`**
- **How it works**: Connects to the popular **Dabble** smartphone app by STEMpedia.
- **Features**:
  - **Digital Mode**: Control with D-Pad arrows (Up, Down, Left, Right).
  - **Analog Mode**: Full variable-speed dual-axis Joystick for smooth driving.
  - **Buttons**:
    - `Triangle` = Turbo High Speed.
    - `Circle` = Precision Slow Crawl.
    - `Cross` = Emergency Stop.
    - `Start` = Trigger Autonomous Line Following.
  - **Collision Prevention**: Ultrasonic sensor halts motors if an obstacle is ahead.

---

## 3. Web Face Screen & AI Receptionist

📁 **`WebApp_Screen/index.html`**
- Designed to run on a tablet, smartphone, or HDMI display mounted on the robot's head.
- **Active Default Face**: **Nordic Capsule** (minimalist Bauhaus glowing cyan pill eyes with inset tracking pupils, dynamic smiling morphing, and real-time audio lip-sync).
- **Features**:
  - **Bilingual Arabic & English**: Speaks Egyptian Arabic (`ar-EG-SalmaNeural`) and English (`en-US-AvaNeural`).
  - **Offline Resilience**: If Wi-Fi drops, the local knowledge base instantly answers questions about E-JUST, President Prof. Ahmed El-Sabbagh, and IEEE RAS with zero cloud latency.
  - **Bluetooth Pairing**: Tap the **● BLE: TAP TO PAIR** badge at the top-left to connect to the ESP32 in 1 click!

---

## 4. Local AI Relay Bridge (PC Server)

📁 **`Antigravity_Local_Relay_Bridge.py`**
- Runs on your laptop/workstation on port 8080.
- Serves the web screen and forwards AI chat requests to Gemini 2.5/Flash while generating studio-grade Edge TTS audio.
- **One-Click Launch**: Double-click **`Start_Antigravity_Local_Relay_Bridge.bat`**.

---

## 5. 3D Print Files & CAD Models

- **`STL_3D_Print_Files/`**: Clean STL files ready to slice in Cura/PrusaSlicer (Drive Base, Torso NFC Dock, Humanoid Head Shell, Shoulder Brackets).
- **`CAD/SolidWorks_Parts/`**: Full editable SolidWorks parts and universal `.STEP` assembly files.

---

*IEEE RAS Student Branch — Egypt-Japan University of Science and Technology (E-JUST)*
