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
 * Live Telemetry in Serial Monitor (Every 300ms):
 *   [SENSORS] Front US | Back US | IR [L C R] | NFC Status | State | Active VIP
 * 
 * Smart IR Line-Lock Mission Cycle:
 *   1. [IDLE] Waits for VIP card tap while streaming ALL sensors live.
 *   2. [NFC TAP] Reads VIP Card -> CHECKS IR SENSORS FIRST:
 *      - If ALREADY ON TAPE (C or L or R): Begins following line IMMEDIATELY! (No spin).
 *      - If OFF TAPE (!L && !C && !R): Spins 90° WHILE MONITORING IR -> Locks onto line
 *        the millisecond center IR catches the black tape!
 *   3. [OUTBOUND] Follows black line using exact compound logic + Front/Rear safety.
 *   4. [ENDPOINT] Tape ends -> Pauses 2s -> Spins 180° until line is re-acquired.
 *   5. [RETURN] Follows line back to startpoint -> When tape ends, stops cleanly.
 *   6. [STANDBY] Cycles back to IDLE ready for next guest!
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
#define ON_LINE HIGH // HIGH (1) when TCRT5000 detects black line

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
// 2. SPEED & TIME CALIBRATIONS
// ======================================================================================
#define SPEED_CRUISE       165   // Forward line following speed (0-255)
#define SPEED_TURN         195   // Turn steering speed for curves (0-255)
#define SPEED_SPIN         200   // Turn-in-place spin speed (0-255)

#define TIME_SPIN_90       1200  // Maximum timeout (ms) to find tape when spinning 90°
#define TIME_SPIN_180      2200  // Maximum timeout (ms) to turn around at endpoint
#define OBSTACLE_DISTANCE  15    // Stop distance threshold (cm)
#define LINE_LOST_MS       450   // ms without tape before declaring endpoint reached
#define TELEMETRY_INTERVAL 300   // ms between continuous serial telemetry prints

// ======================================================================================
// 3. REGISTERED VIP GUEST CARDS TABLE (Sheet2 + Official Replacements)
// ======================================================================================
struct VIPCard {
    const char* code;
    const char* name;
    uint8_t id;
};

const VIPCard VIP_CARDS[] = {
    {"53D30572420001", "Ahmed Elsabagh", 1},
    {"53D80572420001", "Amr Eltawil", 2},
    {"53DA0572420001", "Fukoda", 3},
    {"53D90572420001", "Haitham El-Hussieny", 4},
    {"53DB0572420001", "Maha Elsabrouty", 5},
    {"53C80572420001", "Ahmed M.R. Fath EL-Bab", 6},
    {"53C30572420001", "Ayman Nada", 7},
    {"53C10572420001", "Sameh Sherif", 8},
    {"53C90572420001", "Mohamed Nasef", 9},
    {"53C20572420001", "Wael Khaireldin", 10},
    {"53CA0572420001", "Mohamed Gouda", 11},
    {"53BB0572420001", "Mohamed Adel", 12},
    {"53D00572420001", "Ahmed Abd El-Malek", 13},
    // Fallback entries for remaining cards
    {"53B80572420001", "VIP Guest 14", 14},
    {"53B90572420001", "VIP Guest 15", 15},
    {"53BA0572420001", "VIP Guest 16", 16},
    {"53C00572420001", "VIP Guest 17", 17},
    {"53CB0572420001", "VIP Guest 18", 18},
    {"53D10572420001", "VIP Guest 19", 19},
    {"53D20572420001", "VIP Guest 20", 20},
    {"53E00572420001", "VIP Guest 21", 21}
};
const int TOTAL_VIP_CARDS = sizeof(VIP_CARDS) / sizeof(VIP_CARDS[0]);

MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);

// Helper to normalize card UIDs (strip colons, dashes, and whitespace)
String normalizeUid(const String& raw) {
    String clean = "";
    for (size_t i = 0; i < raw.length(); i++) {
        char c = raw[i];
        if (c != ':' && c != '-' && c != ' ') {
            clean += (char)toupper(c);
        }
    }
    return clean;
}

// ======================================================================================
// 4. ROBOT STATES & TIMERS
// ======================================================================================
enum EscortState {
    STATE_IDLE,              // Waiting for guest to tap card
    STATE_SPIN_90,           // Turning to find and lock onto black tape
    STATE_ESCORT_OUTBOUND,   // Following black tape toward endpoint
    STATE_ENDPOINT_PAUSE,    // Arrived at endpoint: pause before returning
    STATE_SPIN_180,          // Turning 180 degrees to face back
    STATE_ESCORT_RETURN      // Following line back to startpoint
};

EscortState currentState = STATE_IDLE;

unsigned long stateStartTime = 0;
unsigned long lineLostStartTime = 0;
unsigned long lastNfcScanTime = 0;
unsigned long lastTelemetryPrint = 0;
bool lineLostActive = false;
int activeGuestId = 0;
String activeGuestName = "NONE";

// Using int signature to prevent Arduino IDE preprocessor forward declaration bugs
const char* stateStr(int s) {
    switch (s) {
        case STATE_IDLE:            return "IDLE";
        case STATE_SPIN_90:         return "SPIN_90";
        case STATE_ESCORT_OUTBOUND: return "OUTBOUND";
        case STATE_ENDPOINT_PAUSE:  return "ENDPOINT_PAUSE";
        case STATE_SPIN_180:        return "SPIN_180";
        case STATE_ESCORT_RETURN:   return "RETURN";
        default:                    return "UNKNOWN";
    }
}

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
// 6. ULTRASONIC SENSOR (cm)
// ======================================================================================
int distanceCM(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    unsigned long duration = pulseIn(echoPin, HIGH, 20000); // 20ms timeout (~3.4m)
    if (duration == 0) return 999;
    int cm = duration / 58;
    return (cm <= 0) ? 999 : cm;
}

int readDistanceCM(int trigPin, int echoPin) {
    return distanceCM(trigPin, echoPin);
}

// ======================================================================================
// 7. LINE TRACKING STEP & SAFETY LOGIC
// ======================================================================================
// Returns true while line is active; returns false when tape is lost (endpoint)
bool stepLineFollowing() {
    // 1. Front Obstacle Safety Check (< 15 cm)
    int frontDist = distanceCM(F_TRIG, F_ECHO);
    if (frontDist < OBSTACLE_DISTANCE) {
        stopMotors();
        Serial.printf("[FRONT SAFETY] Obstacle ahead (%d cm < %d cm)! Paused...\n", frontDist, OBSTACLE_DISTANCE);
        return true; // Paused safely, mission resumes when cleared
    }

    // 2. Read 3-Channel TCRT5000 IR Line Sensors (ON_LINE = LOW on black tape)
    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE);
    bool R = (digitalRead(IR_R) == ON_LINE);

    // 3. Exact User Compound Line Tracking & Rear Safety Logic
    if (!L && C && !R) {
        // Line centered directly under center sensor -> cruise forward
        setMotors(SPEED_CRUISE, SPEED_CRUISE);
        lineLostActive = false;
    }
    else if ((L && !R && C) || (L && !R && !C)) {
        // Line under left sensor (drifting right) -> steer left
        setMotors(SPEED_CRUISE / 2, SPEED_TURN);
        lineLostActive = false;
    }
    else if ((R && !L && C) || (R && !L && !C)) {
        // Line under right sensor (drifting left) -> steer right
        setMotors(SPEED_TURN, SPEED_CRUISE / 2);
        lineLostActive = false;
    }
    else if (L && C && R) {
        // All sensors on black tape (station line / wide cross marker) -> cruise smoothly
        setMotors(SPEED_CRUISE, SPEED_CRUISE);
        lineLostActive = false;
    }
    else if (!L && !C && !R) {
        // No line detected under any sensor! Check rear clearance
        if (distanceCM(B_TRIG, B_ECHO) > OBSTACLE_DISTANCE) {
            // Safe clearance behind robot (> OBSTACLE_DISTANCE)
            if (!lineLostActive) {
                lineLostActive = true;
                lineLostStartTime = millis();
            } else if (millis() - lineLostStartTime >= LINE_LOST_MS) {
                // Confirmed end of black tape reached safely!
                stopMotors();
                lineLostActive = false;
                return false; // Reached endpoint!
            }
            // Creep forward slowly to verify if tape really ended
            setMotors(SPEED_CRUISE / 2, SPEED_CRUISE / 2);
        } else {
            // Obstacle detected behind robot (<= OBSTACLE_DISTANCE)
            stopMotors();
            Serial.printf("[REAR SAFETY] Obstacle detected behind (%d cm <= %d cm)! Motors halted.\n",
                          distanceCM(B_TRIG, B_ECHO), OBSTACLE_DISTANCE);
        }
    }
    else {
        // Fallback smooth drive
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

    // Format with colons for clean Serial display (e.g. 53:DA:05:72:42:00:01)
    String formattedUid = "";
    for (size_t i = 0; i < uidStr.length(); i++) {
        formattedUid += uidStr[i];
        if (i % 2 == 1 && i < uidStr.length() - 1) formattedUid += ":";
    }

    Serial.println("\n=======================================================");
    Serial.printf(">>> [NFC SCANNED] Card UID: %s (%s)\n", formattedUid.c_str(), uidStr.c_str());

    int matchedIdx = -1;
    for (int i = 0; i < TOTAL_VIP_CARDS; i++) {
        if (uidStr.equalsIgnoreCase(normalizeUid(VIP_CARDS[i].code))) {
            matchedIdx = i;
            break;
        }
    }

    if (matchedIdx >= 0) {
        activeGuestId = VIP_CARDS[matchedIdx].id;
        activeGuestName = VIP_CARDS[matchedIdx].name;
        Serial.printf(">>> [VIP VERIFIED] Welcome %s (Guest ID: %d)!\n", activeGuestName.c_str(), activeGuestId);
        Serial.println("=======================================================\n");
        return true;
    } else {
        Serial.printf(">>> [NFC UNKNOWN] Unregistered Card: %s (Access Denied)\n", formattedUid.c_str());
        Serial.println("=======================================================\n");
        return false;
    }
}

// ======================================================================================
// 9. CONTINUOUS SENSOR & NFC TELEMETRY (SERIAL MONITOR)
// ======================================================================================
void printSensorTelemetry() {
    int fDist = distanceCM(F_TRIG, F_ECHO);
    int bDist = distanceCM(B_TRIG, B_ECHO);

    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE);
    bool R = (digitalRead(IR_R) == ON_LINE);

    byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    const char* nfcStatus = (v == 0x00 || v == 0xFF) ? "OFFLINE" : "READY";

    // Unambiguous live telemetry stream of ALL sensors
    Serial.printf("[SENSORS] Front: %3d cm | Back: %3d cm | IR: [L:%d C:%d R:%d] (%s-%s-%s) | NFC: %-7s | State: %-14s | VIP: %s\n",
                  fDist, bDist,
                  L ? 1 : 0, C ? 1 : 0, R ? 1 : 0,
                  L ? "ON" : "OFF",
                  C ? "ON" : "OFF",
                  R ? "ON" : "OFF",
                  nfcStatus,
                  stateStr(currentState),
                  activeGuestName.c_str());
}

// ======================================================================================
// 10. SETUP
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

    // Initial Health Diagnostic Print of ALL Sensors
    Serial.println("\n--- HARDWARE SENSOR HEALTH CHECK ---");
    Serial.printf("  Front Ultrasonic (Trig %d, Echo %d) : %d cm\n", F_TRIG, F_ECHO, distanceCM(F_TRIG, F_ECHO));
    Serial.printf("  Back Ultrasonic  (Trig %d, Echo %d) : %d cm\n", B_TRIG, B_ECHO, distanceCM(B_TRIG, B_ECHO));
    Serial.printf("  IR Left   (Pin %d) : Raw=%d (%s)\n", IR_L, digitalRead(IR_L), (digitalRead(IR_L) == ON_LINE) ? "ON TAPE" : "OFF TAPE");
    Serial.printf("  IR Center (Pin %d) : Raw=%d (%s)\n", IR_C, digitalRead(IR_C), (digitalRead(IR_C) == ON_LINE) ? "ON TAPE" : "OFF TAPE");
    Serial.printf("  IR Right  (Pin %d) : Raw=%d (%s)\n", IR_R, digitalRead(IR_R), (digitalRead(IR_R) == ON_LINE) ? "ON TAPE" : "OFF TAPE");
    Serial.printf("  NFC Reader (SDA %d): %s (Version: 0x%02X)\n", NFC_SS_PIN, (nfcVer == 0x00 || nfcVer == 0xFF) ? "FAIL/OFFLINE" : "READY", nfcVer);
    Serial.println("------------------------------------\n");

    Serial.println("=======================================================");
    Serial.println("  SYSTEM READY — STANDBY FOR VIP CARD TAP");
    Serial.println("=======================================================\n");

    currentState = STATE_IDLE;
}

// ======================================================================================
// 11. MAIN AUTONOMOUS LOOP
// ======================================================================================
void loop() {
    unsigned long now = millis();

    // 1. Continuous Live Serial Monitor Telemetry (Every 300ms)
    if (now - lastTelemetryPrint >= TELEMETRY_INTERVAL) {
        lastTelemetryPrint = now;
        printSensorTelemetry();
    }

    // 2. Autonomous Escort Mission State Machine
    switch (currentState) {

        // ---------- 1. IDLE: WAITING FOR GUEST CARD ----------
        case STATE_IDLE: {
            if (checkNfcTap()) {
                stopMotors();
                delay(600); // Brief greeting pause

                // CHECK IR SENSORS FIRST!
                bool L = (digitalRead(IR_L) == ON_LINE);
                bool C = (digitalRead(IR_C) == ON_LINE);
                bool R = (digitalRead(IR_R) == ON_LINE);

                Serial.printf("\n[IR CHECK ON TAP] Sensors: Left=%d, Center=%d, Right=%d\n", L ? 1 : 0, C ? 1 : 0, R ? 1 : 0);

                if (C || L || R) {
                    // Robot is ALREADY sitting on the black line! Follow line directly without spinning!
                    Serial.println("[START] Robot is already aligned on black tape! Following line directly...");
                    currentState = STATE_ESCORT_OUTBOUND;
                    lineLostActive = false;
                } else {
                    // Robot is off the line (facing guest). Spin to find the line!
                    Serial.println("[START] Robot off tape -> Spinning 90° to find and lock onto black tape...");
                    stateStartTime = millis();
                    currentState = STATE_SPIN_90;
                }
            }
            break;
        }

        // ---------- 2. SPIN 90 DEGREES TO LINE (SMART IR LOCK) ----------
        case STATE_SPIN_90: {
            // Spin turn towards line
            setMotors(SPEED_SPIN, -SPEED_SPIN);

            // Check IR sensors while spinning:
            bool C = (digitalRead(IR_C) == ON_LINE);
            bool L = (digitalRead(IR_L) == ON_LINE);
            bool R = (digitalRead(IR_R) == ON_LINE);

            // After turning for at least 250ms (clears initial stationary contact),
            // if ANY sensor catches black tape, STOP and start line following!
            if ((now - stateStartTime > 250) && (C || L || R)) {
                stopMotors();
                delay(200);
                Serial.println("[LINE LOCKED] IR sensor caught black tape! Following line to destination...");
                currentState = STATE_ESCORT_OUTBOUND;
                lineLostActive = false;
                break;
            }

            // Safety timeout fallback
            if (now - stateStartTime >= TIME_SPIN_90) {
                stopMotors();
                delay(200);
                Serial.println("[TIMEOUT] 90° spin timeout reached. Attempting line following...");
                currentState = STATE_ESCORT_OUTBOUND;
                lineLostActive = false;
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

        // ---------- 5. SPIN 180 DEGREES TO RETURN (SMART IR LOCK) ----------
        case STATE_SPIN_180: {
            setMotors(SPEED_SPIN, -SPEED_SPIN);

            // Check IR sensors while spinning 180°:
            bool C = (digitalRead(IR_C) == ON_LINE);
            bool L = (digitalRead(IR_L) == ON_LINE);
            bool R = (digitalRead(IR_R) == ON_LINE);

            // After 1000ms of turning, as soon as tape is detected, lock onto line:
            if ((now - stateStartTime > 1000) && (C || L || R)) {
                stopMotors();
                delay(200);
                Serial.println("[LINE LOCKED] Tape detected after 180° spin! Returning to startpoint...");
                currentState = STATE_ESCORT_RETURN;
                lineLostActive = false;
                break;
            }

            if (now - stateStartTime >= TIME_SPIN_180) {
                stopMotors();
                delay(200);
                Serial.println("[TIMEOUT] 180° spin timeout. Returning to startpoint...");
                currentState = STATE_ESCORT_RETURN;
                lineLostActive = false;
            }
            break;
        }

        // ---------- 6. ESCORT RETURN (FOLLOW LINE BACK TO START) ----------
        case STATE_ESCORT_RETURN: {
            bool onLine = stepLineFollowing();
            if (!onLine) {
                // Returned back to startpoint where tape ends!
                stopMotors();
                activeGuestId = 0;
                activeGuestName = "NONE";
                currentState = STATE_IDLE;
                Serial.println("\n[CYCLE COMPLETE] Back at startpoint! Ready for next VIP guest.\n");
            }
            break;
        }
    }

    delay(10); // Smooth RTOS scheduling yield
}
