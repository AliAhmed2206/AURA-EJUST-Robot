/*
 * ======================================================================================
 * AURA-EJUST — DABBLE GAMEPAD FIRMWARE (ESP32 DevKit V1)
 * ======================================================================================
 * Allows full remote manual driving of the VIP Humanoid Robot using the "Dabble" mobile app
 * from STEMpedia (iOS / Android) over Bluetooth Low Energy (BLE).
 *
 * Supported Dabble Modules:
 *   1. GamePad Digital Mode: Directional D-Pad (Up, Down, Left, Right) + Action Buttons
 *   2. GamePad Analog Mode: Fluid Dual-Axis Joystick (Variable Speed Differential Drive)
 *
 * Integrated Hardware & Safety:
 *   - L298N Dual H-Bridge Driver (4 DC Motors)
 *   - HC-SR04 Ultrasonic Collision Sensor (Automatic Safety Brake if obstacle < 35 cm)
 *   - MFRC522 NFC Reader (SPI) — 21 Pre-loaded VIP Cards (7-byte & 4-byte UIDs)
 *   - TCRT5000 IR Sensors (Autonomous Line Escort mode triggerable via Start button)
 *
 * How to Connect:
 *   1. Install "Dabble - Bluetooth Controller" from Google Play Store or Apple App Store.
 *   2. Install "DabbleESP32" library in Arduino IDE (Tools -> Manage Libraries -> DabbleESP32).
 *   3. Open Dabble App -> Tap Bluetooth icon -> Select "AURA_Dabble_Bot" -> Open "GamePad".
 * ======================================================================================
 */

#define CUSTOM_SETTINGS
#define INCLUDE_GAMEPAD_MODULE
#include <DabbleESP32.h>
#include <SPI.h>
#include <MFRC522.h>

// ======================================================================================
// 1. PIN DEFINITIONS (ESP32 DevKit V1)
// ======================================================================================

// L298N Dual H-Bridge Motor Driver (4 DC Motors)
#define MOTOR_ENA_PIN   25    // Left Motors PWM Speed (0-255)
#define MOTOR_IN1_PIN   26    // Left Motors Dir 1
#define MOTOR_IN2_PIN   27    // Left Motors Dir 2
#define MOTOR_IN3_PIN   14    // Right Motors Dir 1
#define MOTOR_IN4_PIN   12    // Right Motors Dir 2
#define MOTOR_ENB_PIN   13    // Right Motors PWM Speed (0-255)

// MFRC522 NFC Reader (Hardware VSPI)
#define NFC_SS_PIN      5     // SDA / SS
#define NFC_RST_PIN     21    // Reset pin
// SPI Default Pins: SCK=18, MISO=19, MOSI=23

// IR Line Tracking Sensors (1 or 2 Sensors)
#define IR_LEFT_PIN     34    // Left IR Sensor (Input Only pin)
#define IR_RIGHT_PIN    35    // Right IR Sensor (Input Only pin, set to -1 if using only 1 IR)
#define LINE_ACTIVE     LOW   // LOW when sensor sees black line

// HC-SR04 Ultrasonic Sensors (Front Obstacle Collision Safety)
#define TRIG_PIN_1      2     // Front Ultrasonic Trig
#define ECHO_PIN_1      4     // Front Ultrasonic Echo
#define TRIG_PIN_2      16    // Optional 2nd Ultrasonic Trig (-1 if not connected)
#define ECHO_PIN_2      17    // Optional 2nd Ultrasonic Echo (-1 if not connected)

// Safety Thresholds
#define OBSTACLE_STOP_CM    35    // Emergency stop distance (cm)

// Driving Speeds
int normalDriveSpeed = 160;   // Default drive PWM (0-255)
int turboDriveSpeed  = 230;   // Turbo drive PWM (Triangle button)
int precisionSpeed   = 100;   // Precision drive PWM (Circle button)
int activeMaxSpeed   = 160;

// ======================================================================================
// 2. 21 REGISTERED SUMMIT NFC CARDS (Clean ID Numbering: VIP Guest 1 .. 21)
// ======================================================================================
struct VIPCard {
    const char* code;
    uint8_t id;
};

const VIPCard VIP_CARDS[] = {
    {"53B80572420001", 1},
    {"53B90572420001", 2},
    {"53BA0572420001", 3},
    {"53BB0572420001", 4},
    {"53C00572420001", 5},
    {"53C10572420001", 6},
    {"53C20572420001", 7},
    {"53C30572420001", 8},
    {"53C80572420001", 9},
    {"53C90572420001", 10},
    {"53CA0572420001", 11},
    {"53CB0572420001", 12},
    {"53D00572420001", 13},
    {"53D10572420001", 14},
    {"53D20572420001", 15},
    {"53D30572420001", 16},
    {"53D80572420001", 17},
    {"53D90572420001", 18},
    {"53DA0572420001", 19},
    {"53DB0572420001", 20},
    {"53E00572420001", 21}
};
const int TOTAL_VIP_CARDS = sizeof(VIP_CARDS) / sizeof(VIP_CARDS[0]);

// ======================================================================================
// 3. OBJECTS & STATE VARIABLES
// ======================================================================================
MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);

enum DriveMode { MODE_MANUAL_DABBLE, MODE_AUTO_LINE_ESCORT };
DriveMode currentMode = MODE_MANUAL_DABBLE;

unsigned long lastNfcScanTime = 0;
unsigned long lastTelemetryTime = 0;
bool obstacleActive = false;

// Forward Declarations
void setMotors(int leftSpeed, int rightSpeed);
void stopMotors();
long getMinObstacleDistance();
void checkNfcReader();
void handleDabbleGamepad();
void runAutonomousLineEscort();

// ======================================================================================
// 4. MOTOR CONTROL
// ======================================================================================
void setMotors(int leftSpeed, int rightSpeed) {
    if (leftSpeed >= 0) {
        digitalWrite(MOTOR_IN1_PIN, HIGH);
        digitalWrite(MOTOR_IN2_PIN, LOW);
    } else {
        digitalWrite(MOTOR_IN1_PIN, LOW);
        digitalWrite(MOTOR_IN2_PIN, HIGH);
        leftSpeed = -leftSpeed;
    }

    if (rightSpeed >= 0) {
        digitalWrite(MOTOR_IN3_PIN, HIGH);
        digitalWrite(MOTOR_IN4_PIN, LOW);
    } else {
        digitalWrite(MOTOR_IN3_PIN, LOW);
        digitalWrite(MOTOR_IN4_PIN, HIGH);
        rightSpeed = -rightSpeed;
    }

    analogWrite(MOTOR_ENA_PIN, constrain(leftSpeed, 0, 255));
    analogWrite(MOTOR_ENB_PIN, constrain(rightSpeed, 0, 255));
}

void stopMotors() {
    setMotors(0, 0);
}

// ======================================================================================
// 5. ULTRASONIC SENSOR
// ======================================================================================
long readUltrasonicCM(int trigPin, int echoPin) {
    if (trigPin < 0 || echoPin < 0) return 999;
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    long duration = pulseIn(echoPin, HIGH, 22000);
    if (duration == 0) return 999;
    return duration * 0.034 / 2;
}

long getMinObstacleDistance() {
    long d1 = readUltrasonicCM(TRIG_PIN_1, ECHO_PIN_1);
    long d2 = (TRIG_PIN_2 >= 0) ? readUltrasonicCM(TRIG_PIN_2, ECHO_PIN_2) : 999;
    return min(d1, d2);
}

// ======================================================================================
// 6. NFC READER
// ======================================================================================
void checkNfcReader() {
    if (!rfid.PICC_IsNewCardPresent()) return;

    unsigned long now = millis();
    if (now - lastNfcScanTime < 1500) return;

    if (!rfid.PICC_ReadCardSerial()) {
        lastNfcScanTime = now;
        return;
    }
    lastNfcScanTime = now;

    String uidStr = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";
        uidStr += String(rfid.uid.uidByte[i], HEX);
    }
    uidStr.toUpperCase();

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    int matchedIdx = -1;
    for (int i = 0; i < TOTAL_VIP_CARDS; i++) {
        if (uidStr.equalsIgnoreCase(VIP_CARDS[i].code)) {
            matchedIdx = i;
            break;
        }
    }

    if (matchedIdx >= 0) {
        Serial.printf("[NFC VALID] Welcome VIP Guest %d (Code: %s)\n", VIP_CARDS[matchedIdx].id, uidStr.c_str());
    } else {
        Serial.printf("[NFC UNKNOWN] Unregistered Card: %s\n", uidStr.c_str());
    }
}

// ======================================================================================
// 7. DABBLE GAMEPAD HANDLER (DIGITAL & ANALOG JOYSTICK)
// ======================================================================================
void handleDabbleGamepad() {
    Dabble.processInput(); // Fetch latest Bluetooth packet from Dabble app

    // 1. Button Speed Profile Selection
    if (GamePad.isTrianglePressed()) {
        activeMaxSpeed = turboDriveSpeed;  // Turbo Mode
    } else if (GamePad.isCirclePressed()) {
        activeMaxSpeed = precisionSpeed;   // Precision Crawl Mode
    } else {
        activeMaxSpeed = normalDriveSpeed; // Normal Mode
    }

    // 2. Start / Select / Cross Actions
    if (GamePad.isStartPressed()) {
        currentMode = MODE_AUTO_LINE_ESCORT;
        Serial.println("[DABBLE] Switched to Autonomous Line Escort Mode");
        return;
    }
    if (GamePad.isSelectPressed() || GamePad.isCrossPressed()) {
        currentMode = MODE_MANUAL_DABBLE;
        stopMotors();
        Serial.println("[DABBLE] Stopped / Manual Mode Restored");
        return;
    }

    // 3. Obstacle Collision Safety Check
    long dist = getMinObstacleDistance();
    bool obstacleAhead = (dist < OBSTACLE_STOP_CM);

    // 4. Analog Joystick Mode
    // getXaxisData() and getYaxisData() range between -7.0 and 7.0
    float joyX = GamePad.getXaxisData();
    float joyY = GamePad.getYaxisData();

    // Check if joystick is being actively moved (outside 1.0 deadzone)
    if (abs(joyX) > 1.0 || abs(joyY) > 1.0) {
        // Map joystick input to motor PWM
        int fwdSpeed  = map((long)(joyY * 10), -70, 70, -activeMaxSpeed, activeMaxSpeed);
        int turnSpeed = map((long)(joyX * 10), -70, 70, -activeMaxSpeed, activeMaxSpeed);

        // Safety override: prevent forward driving if obstacle is detected
        if (fwdSpeed > 0 && obstacleAhead) {
            stopMotors();
            Serial.printf("[SAFETY] Forward move blocked! Obstacle at %ld cm\n", dist);
            return;
        }

        int leftMotor  = constrain(fwdSpeed + turnSpeed, -255, 255);
        int rightMotor = constrain(fwdSpeed - turnSpeed, -255, 255);

        setMotors(leftMotor, rightMotor);
        return;
    }

    // 5. Digital D-Pad Mode (Buttons)
    if (GamePad.isUpPressed()) {
        if (obstacleAhead) {
            stopMotors();
            Serial.printf("[SAFETY] Move Up blocked! Obstacle at %ld cm\n", dist);
        } else {
            setMotors(activeMaxSpeed, activeMaxSpeed); // Forward
        }
    } else if (GamePad.isDownPressed()) {
        setMotors(-activeMaxSpeed, -activeMaxSpeed);  // Backward
    } else if (GamePad.isLeftPressed()) {
        setMotors(-activeMaxSpeed, activeMaxSpeed);   // Spin Left
    } else if (GamePad.isRightPressed()) {
        setMotors(activeMaxSpeed, -activeMaxSpeed);   // Spin Right
    } else {
        stopMotors(); // No button pressed -> Motors off
    }
}

// ======================================================================================
// 8. AUTONOMOUS LINE ESCORT (TRIGGERED VIA START BUTTON)
// ======================================================================================
void runAutonomousLineEscort() {
    long dist = getMinObstacleDistance();
    if (dist < OBSTACLE_STOP_CM) {
        stopMotors();
        return;
    }

    int leftIR = digitalRead(IR_LEFT_PIN);
    int rightIR = (IR_RIGHT_PIN >= 0) ? digitalRead(IR_RIGHT_PIN) : -1;

    if (rightIR == -1) {
        setMotors(normalDriveSpeed, normalDriveSpeed);
        return;
    }

    bool leftOn = (leftIR == LINE_ACTIVE);
    bool rightOn = (rightIR == LINE_ACTIVE);

    if (leftOn && rightOn) {
        setMotors(normalDriveSpeed, normalDriveSpeed);
    } else if (leftOn && !rightOn) {
        setMotors(normalDriveSpeed - 60, normalDriveSpeed + 40); // Steer left
    } else if (!leftOn && rightOn) {
        setMotors(normalDriveSpeed + 40, normalDriveSpeed - 60); // Steer right
    } else {
        setMotors(normalDriveSpeed, normalDriveSpeed);
    }
}

// ======================================================================================
// 9. SETUP & MAIN LOOP
// ======================================================================================
void setup() {
    Serial.begin(115200);
    Serial.println("\n--- [AURA-EJUST] Dabble Gamepad Controller (ESP32 DevKit V1) ---");

    // Initialize SPI & MFRC522 NFC Reader
    SPI.begin();
    rfid.PCD_Init();
    Serial.println("[NFC] MFRC522 Initialized (SPI: SCK=18, MISO=19, MOSI=23, SS=5)");

    // Initialize Motor Driver Pins
    pinMode(MOTOR_ENA_PIN, OUTPUT);
    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    pinMode(MOTOR_IN3_PIN, OUTPUT);
    pinMode(MOTOR_IN4_PIN, OUTPUT);
    pinMode(MOTOR_ENB_PIN, OUTPUT);
    stopMotors();

    // Initialize IR Sensors
    pinMode(IR_LEFT_PIN, INPUT);
    if (IR_RIGHT_PIN >= 0) pinMode(IR_RIGHT_PIN, INPUT);

    // Initialize Ultrasonic Sensors
    pinMode(TRIG_PIN_1, OUTPUT);
    pinMode(ECHO_PIN_1, INPUT);
    if (TRIG_PIN_2 >= 0) {
        pinMode(TRIG_PIN_2, OUTPUT);
        pinMode(ECHO_PIN_2, INPUT);
    }

    // Initialize Dabble BLE Stack
    Dabble.begin("AURA_Dabble_Bot");
    Serial.println("[DABBLE] BLE Online! Broadcast Name: 'AURA_Dabble_Bot'");
    Serial.printf("[SYSTEM] %d VIP Cards Registered. Ready for Driving.\n", TOTAL_VIP_CARDS);
}

void loop() {
    checkNfcReader();

    if (currentMode == MODE_MANUAL_DABBLE) {
        handleDabbleGamepad();
    } else if (currentMode == MODE_AUTO_LINE_ESCORT) {
        // Allow exiting auto mode with Gamepad buttons
        Dabble.processInput();
        if (GamePad.isSelectPressed() || GamePad.isCrossPressed()) {
            currentMode = MODE_MANUAL_DABBLE;
            stopMotors();
            Serial.println("[DABBLE] Escort Cancelled -> Switched to Manual Mode");
        } else {
            runAutonomousLineEscort();
        }
    }
}
