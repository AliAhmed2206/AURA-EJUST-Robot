/*
 * ======================================================================================
 * AURA-EJUST HUMANOID ROBOT - AUTONOMOUS SAFE FAILSAFE BACKUP FIRMWARE
 * ======================================================================================
 * 100% STANDALONE EMERGENCY & BACKUP FIRMWARE - ZERO WI-FI / ZERO AI DEPENDENCY
 * 
 * Hardware Pinout (Exact Match to Physical Robot Wiring):
 *   - IR Line Tracking:  IR_L=32, IR_C=23, IR_R=22 (LOW = On Black Tape)
 *   - L298N Motors:      L_IN1=14, L_IN2=27, L_EN=25 | R_IN1=26, R_IN2=33, R_EN=13
 *   - Ultrasonics:       Front (TRIG=19, ECHO=35) | Rear (TRIG=18, ECHO=34)
 *   - MFRC522 RC522:     SDA=5, RST=2, SCK=15, MISO=16, MOSI=17
 * 
 * Autonomous Mission Cycle (Multi-Guest 15+ VIPs Rotation):
 *   1. [IDLE] Robot waits at startpoint for VIP NFC card tap.
 *   2. [TAP] Guest scans card -> Welcome message -> Spin 90° to align with black tape.
 *   3. [OUTBOUND] Follows black tape smoothly with ultrasonic obstacle safety (<15cm).
 *   4. [ENDPOINT] Reaches end of tape -> Pauses 2s -> Spins 180° to face back.
 *   5. [RETURN] Follows line back to startpoint -> When tape ends, stops cleanly.
 *   6. [STANDBY] Returns to IDLE ready for the next guest to begin a new cycle!
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>

// ======================================================================================
// 1. PIN DEFINITIONS
// ======================================================================================

// 3-Channel TCRT5000 IR Line Tracking Sensors
#define IR_L 32
#define IR_C 23
#define IR_R 22
#define ON_LINE LOW  // LOW when sensor detects black line

// L298N Dual Motor Driver Pins
#define L_IN1 14
#define L_IN2 27
#define L_EN  25

#define R_IN1 26
#define R_IN2 33
#define R_EN  13

// Dual HC-SR04 Ultrasonic Distance Sensors
#define F_TRIG 19
#define F_ECHO 35
#define B_TRIG 18
#define B_ECHO 34

// MFRC522 RFID Card Reader (Custom SPI Pins)
#define NFC_SS_PIN    5     // RC522 SDA / SS -> D5 (GPIO 5)
#define NFC_RST_PIN   2     // RC522 RST      -> D2 (GPIO 2)
#define NFC_SCK_PIN   15    // RC522 SCK      -> D15 (GPIO 15)
#define NFC_MISO_PIN  16    // RC522 MISO     -> RX2 (GPIO 16)
#define NFC_MOSI_PIN  17    // RC522 MOSI     -> TX2 (GPIO 17)

// ======================================================================================
// 2. SPEED & TIME CALIBRATIONS (Tweak here if needed)
// ======================================================================================
#define SPEED_CRUISE       165   // Cruising forward line speed (0-255)
#define SPEED_TURN         195   // Turn steering speed for curves (0-255)
#define SPEED_SPIN         200   // Turn-in-place spin speed (0-255)

#define TIME_SPIN_90       1050  // ms to spin 90 degrees to align with line
#define TIME_SPIN_180      2100  // ms to spin 180 degrees at endpoint to turn around
#define OBSTACLE_DISTANCE  15    // Stop distance threshold (cm)
#define LINE_LOST_MS       450   // ms without tape before declaring endpoint reached

// ======================================================================================
// 3. 21 REGISTERED VIP GUEST CARDS
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

MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);

// ======================================================================================
// 4. ROBOT STATES & TIMERS
// ======================================================================================
enum EscortState {
    STATE_IDLE,              // Waiting for guest to tap card
    STATE_SPIN_90,           // Turning 90 degrees to face black tape
    STATE_ESCORT_OUTBOUND,   // Following black tape toward endpoint
    STATE_ENDPOINT_PAUSE,    // Arrived at endpoint: pause before returning
    STATE_SPIN_180,          // Turning 180 degrees to face back
    STATE_ESCORT_RETURN      // Following line back to startpoint
};

EscortState currentState = STATE_IDLE;

unsigned long stateStartTime = 0;
unsigned long lineLostStartTime = 0;
unsigned long lastNfcScanTime = 0;
unsigned long lastStatusPrint = 0;
bool lineLostActive = false;
int activeGuestId = 0;

// ======================================================================================
// 5. MOTOR PWM DRIVER (ESP32 Core 2.x & 3.x Universal)
// ======================================================================================
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
void setupPWM(int pin, int ch) {
    ledcAttach(pin, 1000, 8);
}
void motorPWM(int pin, int ch, int speed) {
    ledcWrite(pin, constrain(speed, 0, 255));
}
#else
void setupPWM(int pin, int ch) {
    ledcSetup(ch, 1000, 8);
    ledcAttachPin(pin, ch);
}
void motorPWM(int pin, int ch, int speed) {
    ledcWrite(ch, constrain(speed, 0, 255));
}
#endif

void setMotors(int leftSpeed, int rightSpeed) {
    leftSpeed = constrain(leftSpeed, -255, 255);
    rightSpeed = constrain(rightSpeed, -255, 255);

    // Left Motors
    digitalWrite(L_IN1, leftSpeed > 0 ? HIGH : LOW);
    digitalWrite(L_IN2, leftSpeed < 0 ? HIGH : LOW);
    motorPWM(L_EN, 0, abs(leftSpeed));

    // Right Motors
    digitalWrite(R_IN1, rightSpeed > 0 ? HIGH : LOW);
    digitalWrite(R_IN2, rightSpeed < 0 ? HIGH : LOW);
    motorPWM(R_EN, 1, abs(rightSpeed));
}

void stopMotors() {
    setMotors(0, 0);
}

// ======================================================================================
// 6. ULTRASONIC SENSOR
// ======================================================================================
int readDistanceCM(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    unsigned long duration = pulseIn(echoPin, HIGH, 15000); // 15ms timeout ~2.5m
    if (duration == 0) return 999;
    return duration / 58;
}

// ======================================================================================
// 7. LINE TRACKING STEP
// ======================================================================================
// Returns true while line is active; returns false when tape is lost (endpoint)
bool stepLineFollowing() {
    int frontDist = readDistanceCM(F_TRIG, F_ECHO);
    if (frontDist < OBSTACLE_DISTANCE) {
        stopMotors();
        Serial.printf("[SAFETY] Obstacle ahead (%d cm)! Paused...\n", frontDist);
        return true; // Still on line, just temporarily stopped for safety
    }

    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE);
    bool R = (digitalRead(IR_R) == ON_LINE);

    unsigned long now = millis();

    // Check if line is completely lost (no sensor sees black tape)
    if (!L && !C && !R) {
        if (!lineLostActive) {
            lineLostActive = true;
            lineLostStartTime = now;
        } else if (now - lineLostStartTime >= LINE_LOST_MS) {
            // No tape for more than threshold -> Endpoint reached!
            stopMotors();
            lineLostActive = false;
            return false; // Reached end of tape
        }
        // Creep forward slowly to confirm end of tape
        setMotors(SPEED_CRUISE / 2, SPEED_CRUISE / 2);
        return true;
    } else {
        lineLostActive = false;
    }

    // Line Tracking Steer Logic
    if (C && !L && !R) {
        // Line centered
        setMotors(SPEED_CRUISE, SPEED_CRUISE);
    } else if (L && !R) {
        // Drifting right -> Steer left
        setMotors(SPEED_CRUISE / 2, SPEED_TURN);
    } else if (R && !L) {
        // Drifting left -> Steer right
        setMotors(SPEED_TURN, SPEED_CRUISE / 2);
    } else if (L && C && R) {
        // Cross marker / broad tape -> cruise forward smoothly
        setMotors(SPEED_CRUISE, SPEED_CRUISE);
    } else {
        setMotors(SPEED_CRUISE, SPEED_CRUISE);
    }

    return true;
}

// ======================================================================================
// 8. NFC CARD READER
// ======================================================================================
bool checkNfcTap() {
    if (!rfid.PICC_IsNewCardPresent() && !rfid.PICC_ReadCardSerial()) return false;
    if (!rfid.PICC_ReadCardSerial()) return false;

    unsigned long now = millis();
    if (now - lastNfcScanTime < 1500) return false;
    lastNfcScanTime = now;

    String uidStr = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";
        uidStr += String(rfid.uid.uidByte[i], HEX);
    }
    uidStr.toUpperCase();

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    Serial.print("\n>>> [NFC Scanned] Card Code: ");
    Serial.println(uidStr);

    int matchedIdx = -1;
    for (int i = 0; i < TOTAL_VIP_CARDS; i++) {
        if (uidStr.equalsIgnoreCase(VIP_CARDS[i].code)) {
            matchedIdx = i;
            break;
        }
    }

    if (matchedIdx >= 0) {
        activeGuestId = VIP_CARDS[matchedIdx].id;
        Serial.printf("[NFC VALID] Welcome VIP Guest %d! Starting escort mission...\n", activeGuestId);
        return true;
    } else {
        Serial.printf("[NFC UNKNOWN] Unregistered Card: %s (Access Denied)\n", uidStr.c_str());
        return false;
    }
}

// ======================================================================================
// 9. SETUP
// ======================================================================================
void setup() {
    Serial.begin(115200);
    delay(200);

    Serial.println("\n=======================================================");
    Serial.println("  AURA-EJUST HUMANOID — AUTONOMOUS STANDALONE BACKUP");
    Serial.println("=======================================================");

    // 1. Initialize IR Sensors
    pinMode(IR_L, INPUT);
    pinMode(IR_C, INPUT);
    pinMode(IR_R, INPUT);

    // 2. Initialize Motors
    pinMode(L_IN1, OUTPUT);
    pinMode(L_IN2, OUTPUT);
    pinMode(R_IN1, OUTPUT);
    pinMode(R_IN2, OUTPUT);
    setupPWM(L_EN, 0);
    setupPWM(R_EN, 1);
    stopMotors();

    // 3. Initialize Ultrasonics
    pinMode(F_TRIG, OUTPUT);
    pinMode(F_ECHO, INPUT);
    pinMode(B_TRIG, OUTPUT);
    pinMode(B_ECHO, INPUT);

    // 4. Initialize MFRC522 RC522 Reader (Exact Custom Pins)
    pinMode(NFC_RST_PIN, OUTPUT);
    digitalWrite(NFC_RST_PIN, LOW);
    delay(20);
    digitalWrite(NFC_RST_PIN, HIGH);
    delay(50);

    SPI.end();
    SPI.begin(NFC_SCK_PIN, NFC_MISO_PIN, NFC_MOSI_PIN, NFC_SS_PIN);
    rfid.PCD_Init();
    delay(20);
    rfid.PCD_SetAntennaGain(MFRC522::RxGain_max);

    byte nfcVer = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    Serial.printf("[NFC] RC522 Init (Version: 0x%02X) - Pins: SS=%d, RST=%d, SCK=%d, MISO=%d, MOSI=%d\n",
                  nfcVer, NFC_SS_PIN, NFC_RST_PIN, NFC_SCK_PIN, NFC_MISO_PIN, NFC_MOSI_PIN);

    if (nfcVer == 0x00 || nfcVer == 0xFF) {
        Serial.println("[NFC WARNING] Reader communication failed! Check 3.3V power, GND, and wiring.");
    } else {
        Serial.println("[NFC READY] MFRC522 is listening for VIP cards (1-3 cm range)...");
    }

    Serial.println("=======================================================");
    Serial.println("  SYSTEM READY — STANDBY FOR VIP CARD TAP");
    Serial.println("=======================================================\n");

    currentState = STATE_IDLE;
}

// ======================================================================================
// 10. MAIN AUTONOMOUS LOOP
// ======================================================================================
void loop() {
    unsigned long now = millis();

    switch (currentState) {

        // ---------- 1. IDLE: WAITING FOR GUEST CARD ----------
        case STATE_IDLE: {
            // Periodic Status Print every 3s
            if (now - lastStatusPrint >= 3000) {
                lastStatusPrint = now;
                int frontDist = readDistanceCM(F_TRIG, F_ECHO);
                Serial.printf("[STANDBY] Waiting for VIP card tap... (Front sonar: %d cm)\n", frontDist);
            }

            if (checkNfcTap()) {
                stopMotors();
                delay(800); // 800ms greeting pause
                stateStartTime = millis();
                currentState = STATE_SPIN_90;
                Serial.println("[STEP 1] Spinning 90° to align with black line...");
            }
            break;
        }

        // ---------- 2. SPIN 90 DEGREES TO LINE ----------
        case STATE_SPIN_90: {
            // Spin turn (Right motor backwards, Left motor forwards)
            setMotors(SPEED_SPIN, -SPEED_SPIN);

            if (now - stateStartTime >= TIME_SPIN_90) {
                stopMotors();
                delay(300); // Brief settling pause
                currentState = STATE_ESCORT_OUTBOUND;
                lineLostActive = false;
                Serial.println("[STEP 2] Aligned! Following black line to endpoint...");
            }
            break;
        }

        // ---------- 3. ESCORT OUTBOUND (FOLLOW LINE TO ENDPOINT) ----------
        case STATE_ESCORT_OUTBOUND: {
            bool onLine = stepLineFollowing();
            if (!onLine) {
                // End of tape reached!
                stopMotors();
                stateStartTime = millis();
                currentState = STATE_ENDPOINT_PAUSE;
                Serial.println("\n[STEP 3] Reached endpoint (No more tape)! Arrived at destination.");
            }
            break;
        }

        // ---------- 4. DESTINATION PAUSE ----------
        case STATE_ENDPOINT_PAUSE: {
            stopMotors();
            if (now - stateStartTime >= 2000) { // 2s destination pause
                stateStartTime = millis();
                currentState = STATE_SPIN_180;
                Serial.println("[STEP 4] Spinning 180° to face return direction...");
            }
            break;
        }

        // ---------- 5. SPIN 180 DEGREES TO RETURN ----------
        case STATE_SPIN_180: {
            // Spin turn 180 degrees
            setMotors(SPEED_SPIN, -SPEED_SPIN);

            if (now - stateStartTime >= TIME_SPIN_180) {
                stopMotors();
                delay(300); // Brief settling pause
                currentState = STATE_ESCORT_RETURN;
                lineLostActive = false;
                Serial.println("[STEP 5] Aligned! Returning along black line to startpoint...");
            }
            break;
        }

        // ---------- 6. ESCORT RETURN (FOLLOW LINE BACK TO START) ----------
        case STATE_ESCORT_RETURN: {
            bool onLine = stepLineFollowing();
            if (!onLine) {
                // Returned back to startpoint where tape ends!
                stopMotors();
                currentState = STATE_IDLE;
                Serial.println("\n[CYCLE COMPLETE] Back at startpoint! Ready for next VIP guest.\n");
            }
            break;
        }
    }

    delay(10); // Smooth RTOS scheduling yield
}
