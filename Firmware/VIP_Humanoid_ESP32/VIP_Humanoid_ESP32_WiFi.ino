/*
 * ======================================================================================
 * AURA-EJUST — WI-FI ROBOT HARDWARE CONTROLLER (ESP32 DevKit V1)
 * ======================================================================================
 * High-performance Wi-Fi Edition: Connects to local Wi-Fi or phone hotspot.
 * Eliminates Bluetooth pairing dependencies and distance limits.
 *
 * Hardware Components:
 *   1. ESP32-WROOM-32 DevKit V1
 *   2. MFRC522 NFC Reader (SPI) — 13.56 MHz (21 Official VIP Guest Cards)
 *   3. L298N Motor Driver + 4x 12V DC Motors (Differential Drive)
 *   4. 1 or 2 TCRT5000 IR Sensors (Line Tracking / Destination Station Markers)
 *   5. 1 or 2 HC-SR04 Ultrasonic Sensors (Front Obstacle Collision Safety)
 *   6. Wi-Fi Client -> Antigravity Local Relay Bridge / Cloud Gateway
 * ======================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// ======================================================================================
// 1. WI-FI CREDENTIALS & SECURITY TOKEN CONFIGURATION
// ======================================================================================

// >>> EDIT YOUR WI-FI CREDENTIALS HERE <<<
// You can use your mobile phone hotspot or local venue Wi-Fi:
const char* WIFI_SSID     = "Galaxy A24";       // <-- Replace with your Hotspot / Wi-Fi SSID
const char* WIFI_PASSWORD = "auraejustpassword"; // <-- Replace with your Wi-Fi Password

// Dedicated Security / Auth Token
const char* AURA_AUTH_TOKEN = "AURA-EJUST-VIP-2026-TOKEN";

// Relay Server Address:
// Primary: Local PC IP (fastest, <10ms latency on the same Wi-Fi)
const char* SERVER_BASE_URL = "http://10.211.82.178:8080";

// Fallback: Cloudflare Live Tunnel (use if testing over different networks / 4G)
const char* CLOUD_TUNNEL_URL = "https://put-properties-voltage-attacks.trycloudflare.com";

// ======================================================================================
// 2. PIN DEFINITIONS (ESP32 DevKit V1)
// ======================================================================================

// MFRC522 NFC Reader (Hardware VSPI)
#define NFC_SS_PIN      5     // SDA / SS
#define NFC_RST_PIN     21    // Reset pin
// SPI Default Pins: SCK=18, MISO=19, MOSI=23

// L298N Dual H-Bridge Motor Driver (4 DC Motors)
#define MOTOR_ENA_PIN   25    // Left Motors PWM Speed (0-255)
#define MOTOR_IN1_PIN   26    // Left Motors Dir 1
#define MOTOR_IN2_PIN   27    // Left Motors Dir 2
#define MOTOR_IN3_PIN   14    // Right Motors Dir 1
#define MOTOR_IN4_PIN   12    // Right Motors Dir 2
#define MOTOR_ENB_PIN   13    // Right Motors PWM Speed (0-255)

// IR Line Tracking Sensors (1 or 2 Sensors)
#define IR_LEFT_PIN     34    // Left IR Sensor (Input Only pin)
#define IR_RIGHT_PIN    35    // Right IR Sensor (Input Only pin, set to -1 if using only 1 IR)
#define LINE_ACTIVE     LOW   // LOW when sensor sees black line (adjust if sensor inverted)

// HC-SR04 Ultrasonic Sensors (1 or 2 Sensors)
#define TRIG_PIN_1      2     // Front Ultrasonic Trig
#define ECHO_PIN_1      4     // Front Ultrasonic Echo
#define TRIG_PIN_2      16    // Optional 2nd Ultrasonic Trig (set to -1 if using only 1)
#define ECHO_PIN_2      17    // Optional 2nd Ultrasonic Echo (set to -1 if using only 1)

// Escort Speed & Safety Thresholds
#define BASE_DRIVE_SPEED    150   // Normal line following PWM speed (0-255)
#define TURN_SPEED          120   // Turning adjustment PWM speed
#define OBSTACLE_STOP_CM    35    // Stop motors if obstacle closer than 35 cm

// Polling interval (milliseconds)
#define CMD_POLL_INTERVAL_MS  120 // Fast responsive HTTP polling

// ======================================================================================
// 3. 21 REGISTERED SUMMIT NFC CARDS (Clean ID Numbering: VIP Guest 1 .. 21)
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
// 4. ROBOT STATE MACHINE
// ======================================================================================
enum RobotState { STATE_IDLE, STATE_ESCORTING, STATE_PAUSED, STATE_ARRIVED };
RobotState currentState = STATE_IDLE;

String activeCardUid = "NONE";
String activeGuestName = "VIP Guest";
uint8_t targetMarkers = 1;
uint8_t markersCount = 0;

bool obstacleDetected = false;
unsigned long lastPollTime = 0;
unsigned long lastNfcScanTime = 0;

// Manual Timed Movement State (Directional Voice & Wi-Fi Driving)
unsigned long manualDriveEndTime = 0;
bool manualDriveActive = false;
int curManualLeftSpeed = 0;
int curManualRightSpeed = 0;

// Hardware Objects
MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);
HTTPClient httpClient;
WiFiClient wifiClient;

// Active server endpoint in use
String currentServerUrl = SERVER_BASE_URL;

// Forward Declarations
void setMotors(int leftSpeed, int rightSpeed);
void stopMotors();
void executeManualDrive(int leftSpeed, int rightSpeed, unsigned long durationMs);
void pollRelayCommands();
void postTelemetry(const String& event, const String& extraJson = "");
void handleIncomingCommand(const String& cmd);
long readUltrasonicCM(int trigPin, int echoPin);
long getMinObstacleDistance();
const char* stateStr(RobotState s);

// ======================================================================================
// 5. MOTOR CONTROL
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
// 6. ULTRASONIC & IR SENSORS
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

void executeManualDrive(int leftSpeed, int rightSpeed, unsigned long durationMs) {
    if (leftSpeed > 0 && rightSpeed > 0) {
        long dist = getMinObstacleDistance();
        if (dist < OBSTACLE_STOP_CM) {
            stopMotors();
            manualDriveActive = false;
            Serial.printf("[SAFETY] Forward movement blocked! Obstacle at %ld cm\n", dist);
            postTelemetry("OBSTACLE", ",\"dist\":" + String(dist));
            return;
        }
    }
    curManualLeftSpeed = leftSpeed;
    curManualRightSpeed = rightSpeed;
    setMotors(leftSpeed, rightSpeed);
    manualDriveEndTime = millis() + durationMs;
    manualDriveActive = true;
}

// ======================================================================================
// 7. LINE FOLLOWING & DESTINATION TRACKING
// ======================================================================================
void runEscortStep() {
    long dist = getMinObstacleDistance();

    // 1. Front Obstacle Safety Interruption
    if (dist < OBSTACLE_STOP_CM) {
        stopMotors();
        if (!obstacleDetected) {
            obstacleDetected = true;
            Serial.printf("[OBSTACLE] Distance: %ld cm — Motors Paused\n", dist);
            postTelemetry("OBSTACLE", ",\"dist\":" + String(dist));
        }
        return;
    } else if (obstacleDetected) {
        obstacleDetected = false;
        Serial.printf("[CLEAR] Path Clear (%ld cm) — Resuming Escort\n", dist);
        postTelemetry("CLEAR", ",\"dist\":" + String(dist));
    }

    // 2. Read IR Sensor(s)
    int leftIR = digitalRead(IR_LEFT_PIN);
    int rightIR = (IR_RIGHT_PIN >= 0) ? digitalRead(IR_RIGHT_PIN) : -1;

    // A. Single IR Sensor Mode (Checkpoint marker counter)
    if (rightIR == -1) {
        if (leftIR == LINE_ACTIVE) {
            markersCount++;
            Serial.printf("[MARKER] Station Crossed: %d / %d\n", markersCount, targetMarkers);
            postTelemetry("MARKER", ",\"passed\":" + String(markersCount) + ",\"target\":" + String(targetMarkers));
            if (markersCount >= targetMarkers) {
                stopMotors();
                currentState = STATE_ARRIVED;
                postTelemetry("ARRIVED");
                return;
            }
            delay(350); // debounce marker crossing
        }
        setMotors(BASE_DRIVE_SPEED, BASE_DRIVE_SPEED);
        return;
    }

    // B. Two IR Sensors Mode (Left & Right Differential Line Tracking)
    bool leftOn = (leftIR == LINE_ACTIVE);
    bool rightOn = (rightIR == LINE_ACTIVE);

    if (leftOn && rightOn) {
        // Cross-line Station Marker (T-Junction)
        markersCount++;
        Serial.printf("[MARKER] Cross-line Station: %d / %d\n", markersCount, targetMarkers);
        postTelemetry("MARKER", ",\"passed\":" + String(markersCount) + ",\"target\":" + String(targetMarkers));
        if (markersCount >= targetMarkers) {
            stopMotors();
            currentState = STATE_ARRIVED;
            postTelemetry("ARRIVED");
            return;
        }
        setMotors(BASE_DRIVE_SPEED, BASE_DRIVE_SPEED);
        delay(320); // Roll across marker
    } else if (leftOn && !rightOn) {
        // Drifted right -> Steer Left
        setMotors(BASE_DRIVE_SPEED - 60, BASE_DRIVE_SPEED + 40);
    } else if (!leftOn && rightOn) {
        // Drifted left -> Steer Right
        setMotors(BASE_DRIVE_SPEED + 40, BASE_DRIVE_SPEED - 60);
    } else {
        // Both off line (straight tracking or slight wander)
        setMotors(BASE_DRIVE_SPEED, BASE_DRIVE_SPEED);
    }
}

// ======================================================================================
// 8. NFC SCANNER (Supports 7-byte & 4-byte UIDs)
// ======================================================================================
void checkNfcReader() {
    if (!rfid.PICC_IsNewCardPresent()) return;

    unsigned long now = millis();
    if (now - lastNfcScanTime < 1500) return; // Debounce repeated reads

    if (!rfid.PICC_ReadCardSerial()) {
        lastNfcScanTime = now;
        Serial.println("[NFC] Read error (card pulled away too fast)");
        postTelemetry("NFC_TAP", ",\"valid\":false,\"uid\":\"READ_ERROR\"");
        return;
    }
    lastNfcScanTime = now;

    // Convert UID bytes to uppercase Hex String (e.g. "53B80572420001")
    String uidStr = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";
        uidStr += String(rfid.uid.uidByte[i], HEX);
    }
    uidStr.toUpperCase();
    activeCardUid = uidStr;

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    Serial.print("[NFC Scanned] Code: ");
    Serial.println(uidStr);

    // Check against the 21 official VIP cards
    int matchedIdx = -1;
    for (int i = 0; i < TOTAL_VIP_CARDS; i++) {
        if (uidStr.equalsIgnoreCase(VIP_CARDS[i].code)) {
            matchedIdx = i;
            break;
        }
    }

    if (matchedIdx >= 0) {
        int guestId = VIP_CARDS[matchedIdx].id;
        activeGuestName = "VIP Guest " + String(guestId);
        markersCount = 0;

        Serial.printf("[NFC VALID] Welcome VIP Guest %d (Card: %s)\n", guestId, uidStr.c_str());

        postTelemetry("NFC_TAP", ",\"valid\":true,\"uid\":\"" + uidStr + "\",\"id\":" + String(guestId) + ",\"name\":\"" + activeGuestName + "\"");

        // Start Escorting after brief welcome pause
        delay(1200);
        currentState = STATE_ESCORTING;
    } else {
        Serial.printf("[NFC INVALID] Unknown Card Code: %s\n", uidStr.c_str());
        postTelemetry("NFC_TAP", ",\"valid\":false,\"uid\":\"" + uidStr + "\",\"reason\":\"UNREGISTERED\"");
    }
}

// ======================================================================================
// 9. WI-FI HTTP RELAY COMMUNICATION
// ======================================================================================
void postTelemetry(const String& event, const String& extraJson) {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    String url = currentServerUrl + "/api/esp32/telemetry";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(800);

    long dist = getMinObstacleDistance();
    String payload = "{\"token\":\"" + String(AURA_AUTH_TOKEN) +
                     "\",\"event\":\"" + event +
                     "\",\"state\":\"" + String(stateStr(currentState)) +
                     "\",\"dist\":" + String(dist) +
                     extraJson + "}";

    int code = http.POST(payload);
    if (code > 0) {
        // Serial.printf("[TELEMETRY POST] %s (HTTP %d)\n", event.c_str(), code);
    } else {
        // Serial.printf("[TELEMETRY ERR] %s (code %d)\n", http.errorToString(code).c_str(), code);
    }
    http.end();
}

void pollRelayCommands() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    String url = currentServerUrl + "/api/esp32/command?token=" + String(AURA_AUTH_TOKEN);
    http.begin(url);
    http.setTimeout(600); // 600ms timeout for non-blocking loop

    int httpCode = http.GET();
    if (httpCode == 200) {
        String payload = http.getString();
        // Parse simple JSON: {"cmd": "MOVE_FWD", ...}
        int cmdIdx = payload.indexOf("\"cmd\":");
        if (cmdIdx >= 0) {
            int startQuote = payload.indexOf('"', cmdIdx + 6);
            if (startQuote >= 0) {
                int endQuote = payload.indexOf('"', startQuote + 1);
                if (endQuote >= 0) {
                    String cmd = payload.substring(startQuote + 1, endQuote);
                    if (cmd != "NONE" && cmd.length() > 0) {
                        handleIncomingCommand(payload);
                    }
                }
            }
        }
    }
    http.end();
}

void handleIncomingCommand(const String& cmd) {
    Serial.print("[WI-FI CMD RX] ");
    Serial.println(cmd);

    if (cmd.indexOf("START_ESCORT") >= 0) {
        markersCount = 0;
        currentState = STATE_ESCORTING;
        Serial.println("[CMD] Escort Started via Wi-Fi Command");
        postTelemetry("STATUS");
    } else if (cmd.indexOf("PAUSE") >= 0) {
        stopMotors();
        currentState = STATE_PAUSED;
        Serial.println("[CMD] Escort Paused");
        postTelemetry("STATUS");
    } else if (cmd.indexOf("RESUME") >= 0) {
        currentState = STATE_ESCORTING;
        Serial.println("[CMD] Escort Resumed");
        postTelemetry("STATUS");
    } else if (cmd.indexOf("RESET") >= 0) {
        stopMotors();
        currentState = STATE_IDLE;
        markersCount = 0;
        activeCardUid = "NONE";
        Serial.println("[CMD] System Reset to IDLE");
        postTelemetry("STATUS");
    } else if (cmd.indexOf("MOVE_FWD") >= 0) {
        int duration = 1500;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 1500;
        executeManualDrive(BASE_DRIVE_SPEED, BASE_DRIVE_SPEED, duration);
        Serial.printf("[CMD] Wi-Fi Move Forward (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"MOVE_FWD\"");
    } else if (cmd.indexOf("MOVE_REV") >= 0) {
        int duration = 1500;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 1500;
        executeManualDrive(-BASE_DRIVE_SPEED, -BASE_DRIVE_SPEED, duration);
        Serial.printf("[CMD] Wi-Fi Move Backward (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"MOVE_REV\"");
    } else if (cmd.indexOf("TURN_LEFT") >= 0) {
        int duration = 650;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 650;
        executeManualDrive(-TURN_SPEED, TURN_SPEED, duration);
        Serial.printf("[CMD] Wi-Fi Turn Left (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"TURN_LEFT\"");
    } else if (cmd.indexOf("TURN_RIGHT") >= 0) {
        int duration = 650;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 650;
        executeManualDrive(TURN_SPEED, -TURN_SPEED, duration);
        Serial.printf("[CMD] Wi-Fi Turn Right (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"TURN_RIGHT\"");
    } else if (cmd.indexOf("WAVE") >= 0) {
        Serial.println("[CMD] Wi-Fi Wave Gesture");
        executeManualDrive(-TURN_SPEED / 2, TURN_SPEED / 2, 220);
        delay(250);
        executeManualDrive(TURN_SPEED / 2, -TURN_SPEED / 2, 220);
        postTelemetry("GESTURE", ",\"action\":\"WAVE\"");
    } else if (cmd.indexOf("STOP") >= 0) {
        stopMotors();
        manualDriveActive = false;
        currentState = STATE_IDLE;
        Serial.println("[CMD] Wi-Fi Hard Stop");
        postTelemetry("STATUS");
    }
}

const char* stateStr(RobotState s) {
    switch (s) {
        case STATE_IDLE:      return "IDLE";
        case STATE_ESCORTING: return "ESCORTING";
        case STATE_PAUSED:    return "PAUSED";
        case STATE_ARRIVED:   return "ARRIVED";
        default:              return "IDLE";
    }
}

// ======================================================================================
// 10. SETUP & MAIN LOOP
// ======================================================================================
void setup() {
    Serial.begin(115200);
    Serial.println("\n=======================================================");
    Serial.println("  AURA-EJUST — WI-FI HARDWARE CONTROLLER STARTING");
    Serial.println("=======================================================");

    // 1. Initialize SPI & MFRC522 NFC Reader
    SPI.begin(18, 19, 23, NFC_SS_PIN);
    rfid.PCD_Init();
    delay(4);
    byte v = rfid.PCD_ReadRegister(rfid.VersionReg);
    Serial.printf("[NFC INIT] Reader Chip Version: 0x%02X (%s)\n", v, (v == 0x92 || v == 0x91) ? "OK" : "CHECK WIRING");

    // 2. Initialize Motor Driver Pins
    pinMode(MOTOR_ENA_PIN, OUTPUT);
    pinMode(MOTOR_IN1_PIN, OUTPUT);
    pinMode(MOTOR_IN2_PIN, OUTPUT);
    pinMode(MOTOR_IN3_PIN, OUTPUT);
    pinMode(MOTOR_IN4_PIN, OUTPUT);
    pinMode(MOTOR_ENB_PIN, OUTPUT);
    stopMotors();

    // 3. Initialize IR Line Sensors
    pinMode(IR_LEFT_PIN, INPUT);
    if (IR_RIGHT_PIN >= 0) pinMode(IR_RIGHT_PIN, INPUT);

    // 4. Initialize Ultrasonic Pins
    pinMode(TRIG_PIN_1, OUTPUT);
    pinMode(ECHO_PIN_1, INPUT);
    if (TRIG_PIN_2 >= 0) {
        pinMode(TRIG_PIN_2, OUTPUT);
        pinMode(ECHO_PIN_2, INPUT);
    }

    // 5. Connect to Wi-Fi
    Serial.printf("[WI-FI] Connecting to SSID: %s\n", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 25) {
        delay(400);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n[WI-FI] Connected successfully!");
        Serial.printf("[WI-FI] ESP32 IP Address: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("[WI-FI] Gateway Bridge:   %s\n", currentServerUrl.c_str());
        Serial.printf("[WI-FI] Auth Token:       %s\n", AURA_AUTH_TOKEN);
        postTelemetry("ONLINE", ",\"ip\":\"" + WiFi.localIP().toString() + "\"");
    } else {
        Serial.println("\n[WI-FI WARNING] Connection timed out! Retrying in background loop...");
    }

    Serial.println("=======================================================");
    Serial.println("  SYSTEM READY — WAITING FOR COMMANDS & NFC CARDS");
    Serial.println("=======================================================\n");
}

void loop() {
    unsigned long now = millis();

    // 1. Maintain Wi-Fi Connection
    if (WiFi.status() != WL_CONNECTED) {
        static unsigned long lastReconnectAttempt = 0;
        if (now - lastReconnectAttempt > 5000) {
            lastReconnectAttempt = now;
            Serial.println("[WI-FI] Reconnecting...");
            WiFi.reconnect();
        }
    }

    // 2. Poll for Web/Voice Commands every CMD_POLL_INTERVAL_MS
    if (now - lastPollTime >= CMD_POLL_INTERVAL_MS) {
        lastPollTime = now;
        pollRelayCommands();
    }

    // 3. Handle Timed Manual Driving (Voice navigation: Forward, Left, Right)
    if (manualDriveActive) {
        if (now >= manualDriveEndTime) {
            stopMotors();
            manualDriveActive = false;
            curManualLeftSpeed = 0;
            curManualRightSpeed = 0;
            Serial.println("[MANUAL] Move Duration Finished -> Stopped");
        } else {
            // Front collision brake during manual forward movement
            if (curManualLeftSpeed > 0 && curManualRightSpeed > 0) {
                long dist = getMinObstacleDistance();
                if (dist < OBSTACLE_STOP_CM) {
                    stopMotors();
                    manualDriveActive = false;
                    Serial.printf("[SAFETY] Obstacle detected during manual move (%ld cm)! Stopped\n", dist);
                    postTelemetry("OBSTACLE", ",\"dist\":" + String(dist));
                }
            }
        }
    }

    // 4. Autonomous Line Following & Destination Tracking
    if (currentState == STATE_ESCORTING && !manualDriveActive) {
        runEscortStep();
    }

    // 5. Scan NFC Reader for VIP Cards
    checkNfcReader();

    delay(5); // Small yield for RTOS task scheduler
}
