/*
 * ======================================================================================
 * AURA-EJUST HUMANOID ROBOT - WI-FI TELEMETRY & AUTONOMOUS ESCORT FIRMWARE (ESP32)
 * ======================================================================================
 * Architecture:
 *   - Autonomous Physical Navigation on ESP32 (Zero AI motor lag or dependency)
 *   - Continuous Live Telemetry: Front US | Back US | IR [L C R] | NFC | State | VIP
 *   - Live Wi-Fi Telemetry Streaming to Antigravity Local Relay Bridge / Phone AI Brain
 *   - AI Screen & Voice (AURA) interacts with guests, announces names, and reacts to sensors
 * 
 * Hardware Pinout (Exact Match to Physical Robot Wiring):
 *   - IR Line Tracking:  IR_L=32, IR_C=23, IR_R=22
 *                        (Center IR_C = Middle sensor for the perfect black tape)
 *                        (IR_L & IR_R = Side sensors for steering accuracy)
 *                        (1 = Black Tape, 0 = White Floor)
 *   - L298N Motors:      L_IN1=14, L_IN2=27, L_EN=25 | R_IN1=26, R_IN2=33, R_EN=13
 *   - Ultrasonics:       Front (TRIG=19, ECHO=35) | Rear (TRIG=18, ECHO=34)
 *   - MFRC522 RC522:     SDA=5, RST=2, SCK=15, MISO=16, MOSI=17
 * 
 * Safety & Operation Rules:
 *   - NO blind movement: After scan, motors DO NOT move unless black tape is detected!
 *   - Middle IR (Pin 23) reading (1) = Cruise forward directly along the line!
 *   - Left/Right IR reading (1)     = Precise steering correction (Left/Right)!
 *   - Dual Ultrasonic Safety        = Front (<15cm) & Rear (<15cm) Emergency Stop!
 * ======================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPmDNS.h>
#include <SPI.h>
#include <MFRC522.h>

// ======================================================================================
// 1. WI-FI & SERVER CONFIGURATION
// ======================================================================================
const char* WIFI_SSID       = "Ali";                 // Hotspot name
const char* WIFI_PASSWORD   = "12345679";            // Hotspot password
const char* AURA_AUTH_TOKEN = "AURA-EJUST-VIP-2026-TOKEN";

const char* SERVER_BASE_URL = "http://10.10.227.235:8080";
String currentServerUrl     = SERVER_BASE_URL;

// ======================================================================================
// 2. PIN DEFINITIONS
// ======================================================================================

// 3-Channel TCRT5000 IR Line Tracking Sensors on Front
// Pin 32 = Left IR (Steering accuracy)
// Pin 23 = Center IR (Middle sensor for perfect black tape)
// Pin 22 = Right IR (Steering accuracy)
#define IR_L 32
#define IR_C 23
#define IR_R 22

// Black Tape = 1 (HIGH), White Floor = 0 (LOW)
#define ON_LINE HIGH

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

// MFRC522 RFID Card Reader (Exact Custom Pins)
#define NFC_SS_PIN    5     // RC522 SDA / SS -> D5 (GPIO 5)
#define NFC_RST_PIN   2     // RC522 RST      -> D2 (GPIO 2)
#define NFC_SCK_PIN   15    // RC522 SCK      -> D15 (GPIO 15)
#define NFC_MISO_PIN  16    // RC522 MISO     -> RX2 (GPIO 16)
#define NFC_MOSI_PIN  17    // RC522 MOSI     -> TX2 (GPIO 17)

// ======================================================================================
// 3. SPEED & TIMING CALIBRATIONS
// ======================================================================================
#define SPEED_CRUISE       165   // Forward line following speed (0-255)
#define SPEED_TURN         195   // Turning adjustment on curves (0-255)
#define SPEED_SPIN         200   // Turn-in-place spin speed (0-255)

#define TIME_SPIN_180      2200  // Maximum timeout (ms) to turn around at endpoint
#define OBSTACLE_DISTANCE  15    // Front/Rear obstacle safety threshold (cm)
#define LINE_LOST_MS       450   // ms without tape before declaring endpoint reached
#define TELEMETRY_INTERVAL 400   // Wi-Fi Telemetry streaming interval (ms)
#define SERIAL_PRINT_MS    300   // Serial Monitor telemetry interval (ms)

// ======================================================================================
// 4. REGISTERED VIP GUEST CARDS TABLE (Sheet2 + Official Replacements)
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
// 5. ROBOT STATE MACHINE
// ======================================================================================
enum EscortState {
    STATE_IDLE,              // Waiting for guest card tap and black tape
    STATE_ESCORT_OUTBOUND,   // Following line to destination endpoint
    STATE_ENDPOINT_PAUSE,    // Arrived at destination: 2s pause
    STATE_SPIN_180,          // Turning 180 degrees to face return direction
    STATE_ESCORT_RETURN      // Following line back to startpoint
};

EscortState currentState = STATE_IDLE;

unsigned long stateStartTime       = 0;
unsigned long lineLostStartTime    = 0;
unsigned long lastNfcScanTime      = 0;
unsigned long lastTelemetryTime    = 0;
unsigned long lastSerialPrintTime  = 0;
bool lineLostActive                = false;
int activeGuestId                  = 0;
String activeGuestName             = "NONE";
String activeCardUid               = "NONE";

// Using int signature to prevent Arduino IDE preprocessor forward declaration bugs
const char* stateStr(int s) {
    switch (s) {
        case STATE_IDLE:            return "IDLE";
        case STATE_ESCORT_OUTBOUND: return "ESCORTING";
        case STATE_ENDPOINT_PAUSE:  return "ARRIVED";
        case STATE_SPIN_180:        return "TURNING_180";
        case STATE_ESCORT_RETURN:   return "RETURNING";
        default:                    return "IDLE";
    }
}

// ======================================================================================
// 6. MOTOR & PWM DRIVER
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

    digitalWrite(L_IN1, leftSpeed > 0 ? HIGH : LOW);
    digitalWrite(L_IN2, leftSpeed < 0 ? HIGH : LOW);
    motorPWM(L_EN, 0, abs(leftSpeed));

    digitalWrite(R_IN1, rightSpeed > 0 ? HIGH : LOW);
    digitalWrite(R_IN2, rightSpeed < 0 ? HIGH : LOW);
    motorPWM(R_EN, 1, abs(rightSpeed));
}

void stopMotors() {
    setMotors(0, 0);
}

// ======================================================================================
// 7. SENSOR READINGS
// ======================================================================================
int distanceCM(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    unsigned long duration = pulseIn(echoPin, HIGH, 25000); // 25ms timeout (~4.2m)
    if (duration == 0) return 999;
    int cm = duration / 58;
    return (cm <= 0) ? 999 : cm;
}

int readDistanceCM(int trigPin, int echoPin) {
    return distanceCM(trigPin, echoPin);
}

// ======================================================================================
// 8. WI-FI TELEMETRY TO LOCAL RELAY BRIDGE & AI BRAIN
// ======================================================================================
void postTelemetry(const String& event, const String& extraJson = "") {
    if (WiFi.status() != WL_CONNECTED) return;

    int frontDist = distanceCM(F_TRIG, F_ECHO);
    int backDist  = distanceCM(B_TRIG, B_ECHO);

    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE);
    bool R = (digitalRead(IR_R) == ON_LINE);
    String irStr = String(L ? "1" : "0") + String(C ? "1" : "0") + String(R ? "1" : "0");

    String payload = "{\"token\":\"" + String(AURA_AUTH_TOKEN) +
                     "\",\"event\":\"" + event +
                     "\",\"state\":\"" + String(stateStr(currentState)) +
                     "\",\"dist\":" + String(frontDist) +
                     ",\"back_dist\":" + String(backDist) +
                     ",\"ir\":\"" + irStr + "\"" +
                     ",\"guest\":\"" + activeGuestName + "\"" +
                     extraJson + "}";

    HTTPClient http;
    http.begin(currentServerUrl + "/api/esp32/telemetry");
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(400); // Fast non-blocking timeout
    int code = http.POST(payload);
    http.end();
}

// ======================================================================================
// 9. LINE TRACKING STEP & SAFETY LOGIC
// ======================================================================================
// Returns true while line is active; returns false when tape is lost (endpoint)
bool stepLineFollowing() {
    // 1. FRONT Obstacle Safety Check (< 15 cm)
    int frontDist = distanceCM(F_TRIG, F_ECHO);
    if (frontDist < OBSTACLE_DISTANCE) {
        stopMotors();
        Serial.printf("[FRONT SAFETY] Obstacle ahead (%d cm < %d cm)! Motors halted.\n", frontDist, OBSTACLE_DISTANCE);
        postTelemetry("OBSTACLE", ",\"dist\":" + String(frontDist));
        return true; // Still on line, waiting for obstacle to clear
    }

    // 2. REAR Obstacle Safety Check (< 15 cm)
    int backDist = distanceCM(B_TRIG, B_ECHO);
    if (backDist < OBSTACLE_DISTANCE) {
        stopMotors();
        Serial.printf("[BACK SAFETY] Obstacle behind (%d cm < %d cm)! Motors halted.\n", backDist, OBSTACLE_DISTANCE);
        postTelemetry("OBSTACLE", ",\"back_dist\":" + String(backDist));
        return true; // Still on line, waiting for obstacle to clear
    }

    // 3. Read 3-Channel TCRT5000 IR Line Sensors on Front
    // 1 = Black Tape, 0 = White Floor
    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE); // Middle sensor for perfect black tape
    bool R = (digitalRead(IR_R) == ON_LINE);

    // 4. Exact User Line Tracking Cases
    if (!L && C && !R) {
        // Line centered directly under center sensor (1 in middle) -> cruise forward!
        setMotors(SPEED_CRUISE, SPEED_CRUISE);
        lineLostActive = false;
    }
    else if ((L && !R && C) || (L && !R && !C)) {
        // Line under left sensor (drifting right) -> steer left!
        setMotors(SPEED_CRUISE / 2, SPEED_TURN);
        lineLostActive = false;
    }
    else if ((R && !L && C) || (R && !L && !C)) {
        // Line under right sensor (drifting left) -> steer right!
        setMotors(SPEED_TURN, SPEED_CRUISE / 2);
        lineLostActive = false;
    }
    else if (L && C && R) {
        // All sensors on black tape (station line / wide cross marker) -> cruise smoothly forward!
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
// 10. NFC CARD READER
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
    activeCardUid = uidStr;

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    // Format with colons for clean display (e.g. 53:DA:05:72:42:00:01)
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

        // Notify AI Brain over Wi-Fi so AURA speaks the guest's name aloud!
        postTelemetry("NFC_TAP", ",\"valid\":true,\"uid\":\"" + uidStr + "\",\"id\":" + String(activeGuestId) + ",\"name\":\"" + activeGuestName + "\"");
        return true;
    } else {
        Serial.printf(">>> [NFC UNKNOWN] Unregistered Card: %s (Access Denied)\n", formattedUid.c_str());
        Serial.println("=======================================================\n");
        postTelemetry("NFC_TAP", ",\"valid\":false,\"uid\":\"" + uidStr + "\",\"reason\":\"UNREGISTERED\"");
        return false;
    }
}

// ======================================================================================
// 11. CONTINUOUS SENSOR & NFC TELEMETRY (SERIAL MONITOR)
// ======================================================================================
void printSensorTelemetry() {
    int fDist = distanceCM(F_TRIG, F_ECHO);
    int bDist = distanceCM(B_TRIG, B_ECHO);

    // 1 = Black Tape, 0 = White Floor
    int L = (digitalRead(IR_L) == ON_LINE) ? 1 : 0;
    int C = (digitalRead(IR_C) == ON_LINE) ? 1 : 0; // Middle sensor for perfect black tape
    int R = (digitalRead(IR_R) == ON_LINE) ? 1 : 0;

    byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    const char* nfcStatus = (v == 0x00 || v == 0xFF) ? "OFFLINE" : "READY";

    Serial.printf("[SENSORS] Front: %3d cm | Back: %3d cm | IR: [L:%d C:%d R:%d] | NFC: %-7s | State: %-14s | VIP: %s\n",
                  fDist, bDist,
                  L, C, R,
                  nfcStatus,
                  stateStr(currentState),
                  activeGuestName.c_str());
}

// ======================================================================================
// 12. SETUP
// ======================================================================================
void setup() {
    Serial.begin(115200);
    delay(200);

    Serial.println("\n=======================================================");
    Serial.println("  AURA-EJUST — AUTONOMOUS ESCORT & AI TELEMETRY (ESP32)");
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
    Serial.printf("  IR Left   (Pin %d) : %d (%s)\n", IR_L, (digitalRead(IR_L) == ON_LINE), (digitalRead(IR_L) == ON_LINE) ? "BLACK TAPE (1)" : "WHITE (0)");
    Serial.printf("  IR Center (Pin %d) : %d (%s)\n", IR_C, (digitalRead(IR_C) == ON_LINE), (digitalRead(IR_C) == ON_LINE) ? "BLACK TAPE (1)" : "WHITE (0)");
    Serial.printf("  IR Right  (Pin %d) : %d (%s)\n", IR_R, (digitalRead(IR_R) == ON_LINE), (digitalRead(IR_R) == ON_LINE) ? "BLACK TAPE (1)" : "WHITE (0)");
    Serial.printf("  NFC Reader (SDA %d): %s (Version: 0x%02X)\n", NFC_SS_PIN, (nfcVer == 0x00 || nfcVer == 0xFF) ? "FAIL/OFFLINE" : "READY", nfcVer);
    Serial.println("------------------------------------\n");

    // 5. Connect to Wi-Fi
    Serial.printf("[WI-FI] Connecting to SSID: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 25) {
        delay(350);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WI-FI] Connected successfully!");
        Serial.printf("[WI-FI] ESP32 IP Address: %s\n", WiFi.localIP().toString().c_str());

        // mDNS auto-discovery of laptop bridge
        if (MDNS.begin("aura-robot")) {
            IPAddress pcIP = MDNS.queryHost("Ali-Mohamed", 2000);
            if (pcIP != INADDR_NONE) {
                currentServerUrl = "http://" + pcIP.toString() + ":8080";
                Serial.printf("[mDNS] Found Laptop at %s!\n", currentServerUrl.c_str());
            }
        }
        Serial.printf("[WI-FI] Gateway Bridge: %s\n", currentServerUrl.c_str());
        postTelemetry("ONLINE", ",\"ip\":\"" + WiFi.localIP().toString() + "\"");
    } else {
        Serial.println("\n[WI-FI NOTICE] Continuing in offline autonomous mode...");
    }

    Serial.println("=======================================================");
    Serial.println("  SYSTEM READY — STANDBY FOR VIP GUEST CARD TAP");
    Serial.println("=======================================================\n");

    currentState = STATE_IDLE;
}

// ======================================================================================
// 13. MAIN LOOP (AUTONOMOUS ESCORT + LIVE TELEMETRY)
// ======================================================================================
void loop() {
    unsigned long now = millis();

    // 1. Maintain Wi-Fi Connection
    if (WiFi.status() == WL_DISCONNECTED) {
        static unsigned long lastReconnect = 0;
        if (now - lastReconnect > 8000) {
            lastReconnect = now;
            WiFi.reconnect();
        }
    }

    // 2. Stream Live Wi-Fi Telemetry to AI Brain every 400ms
    if (now - lastTelemetryTime >= TELEMETRY_INTERVAL) {
        lastTelemetryTime = now;
        postTelemetry("HEARTBEAT");
    }

    // 3. Continuous Live Serial Monitor Telemetry every 300ms
    if (now - lastSerialPrintTime >= SERIAL_PRINT_MS) {
        lastSerialPrintTime = now;
        printSensorTelemetry();
    }

    // 4. Autonomous Mission State Machine
    switch (currentState) {

        // ---------- 1. IDLE: WAITING FOR GUEST CARD & BLACK TAPE ----------
        case STATE_IDLE: {
            if (checkNfcTap()) {
                stopMotors();
                Serial.printf("\n>>> [VIP CARD VERIFIED] Welcome %s (Guest ID: %d)!\n", activeGuestName.c_str(), activeGuestId);

                // Check IR Sensors immediately:
                // 1 in middle (C) is responsible for the perfect line
                bool L = (digitalRead(IR_L) == ON_LINE);
                bool C = (digitalRead(IR_C) == ON_LINE);
                bool R = (digitalRead(IR_R) == ON_LINE);

                Serial.printf("[IR ON SCAN] L:%d, C:%d (Center Tape), R:%d\n", L ? 1 : 0, C ? 1 : 0, R ? 1 : 0);

                if (C || L || R) {
                    // Robot sees the black tape!
                    Serial.println("[START] Black tape detected under sensors! Following line in 1 second...");
                    delay(1000);
                    currentState = STATE_ESCORT_OUTBOUND;
                    lineLostActive = false;
                    postTelemetry("STATUS", ",\"action\":\"ESCORTING\"");
                } else {
                    // Robot does NOT see black tape (0 0 0).
                    // RULE: Motors DO NOT move unless it sees the black tape!
                    Serial.println("[NO TAPE DETECTED] All IR sensors are 0. Robot will NOT move until placed on black tape!");
                }
            } else if (activeGuestId > 0) {
                // Card was already scanned, waiting for robot to be aligned on black tape:
                bool L = (digitalRead(IR_L) == ON_LINE);
                bool C = (digitalRead(IR_C) == ON_LINE);
                bool R = (digitalRead(IR_R) == ON_LINE);

                if (C || L || R) {
                    Serial.println("[LINE DETECTED] Black tape detected under center sensor! Starting line following...");
                    delay(500);
                    currentState = STATE_ESCORT_OUTBOUND;
                    lineLostActive = false;
                    postTelemetry("STATUS", ",\"action\":\"ESCORTING\"");
                }
            }
            break;
        }

        // ---------- 2. ESCORT OUTBOUND (FOLLOW LINE TO ENDPOINT) ----------
        case STATE_ESCORT_OUTBOUND: {
            bool onLine = stepLineFollowing();
            if (!onLine) {
                // Reached end of black tape!
                stopMotors();
                stateStartTime = millis();
                currentState = STATE_ENDPOINT_PAUSE;
                Serial.println("\n[STEP 2] Reached endpoint (No more tape)! Arrived at destination.");
                postTelemetry("ARRIVED", ",\"dest\":\"Destination Endpoint\"");
            }
            break;
        }

        // ---------- 3. DESTINATION PAUSE ----------
        case STATE_ENDPOINT_PAUSE: {
            stopMotors();
            if (now - stateStartTime >= 2000) { // 2s destination pause
                stateStartTime = millis();
                currentState = STATE_SPIN_180;
                Serial.println("[STEP 3] Spinning 180° to face return direction...");
                postTelemetry("STATUS", ",\"action\":\"SPIN_180\"");
            }
            break;
        }

        // ---------- 4. SPIN 180 DEGREES TO RETURN (WITH DUAL US SAFETY & LINE LOCK) ----------
        case STATE_SPIN_180: {
            int fDist = distanceCM(F_TRIG, F_ECHO);
            int bDist = distanceCM(B_TRIG, B_ECHO);
            if (fDist < OBSTACLE_DISTANCE || bDist < OBSTACLE_DISTANCE) {
                stopMotors();
                Serial.printf("[SPIN SAFETY] Obstacle nearby (Front:%d cm, Back:%d cm)! Turn paused...\n", fDist, bDist);
                break;
            }

            setMotors(SPEED_SPIN, -SPEED_SPIN);

            // Check IR sensors while spinning 180°:
            bool C = (digitalRead(IR_C) == ON_LINE);
            bool L = (digitalRead(IR_L) == ON_LINE);
            bool R = (digitalRead(IR_R) == ON_LINE);

            if ((now - stateStartTime > 1000) && (C || L || R)) {
                stopMotors();
                delay(200);
                Serial.println("[LINE LOCKED] Tape detected after 180° spin! Returning to startpoint...");
                currentState = STATE_ESCORT_RETURN;
                lineLostActive = false;
                postTelemetry("STATUS", ",\"action\":\"RETURNING\"");
                break;
            }

            if (now - stateStartTime >= TIME_SPIN_180) {
                stopMotors();
                delay(200);
                Serial.println("[TIMEOUT] 180° spin timeout. Returning to startpoint...");
                currentState = STATE_ESCORT_RETURN;
                lineLostActive = false;
                postTelemetry("STATUS", ",\"action\":\"RETURNING\"");
            }
            break;
        }

        // ---------- 5. ESCORT RETURN (FOLLOW LINE BACK TO START) ----------
        case STATE_ESCORT_RETURN: {
            bool onLine = stepLineFollowing();
            if (!onLine) {
                // Returned back to startpoint where tape ends!
                stopMotors();
                activeGuestId = 0;
                activeGuestName = "NONE";
                currentState = STATE_IDLE;
                Serial.println("\n[CYCLE COMPLETE] Back at startpoint! Ready for next VIP guest.\n");
                postTelemetry("STATUS", ",\"state\":\"IDLE\"");
            }
            break;
        }
    }

    delay(10); // Smooth RTOS scheduling yield
}
