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

const char* SERVER_BASE_URL = "http://10.103.194.178:8080";
String currentServerUrl     = SERVER_BASE_URL;

// ======================================================================================
// 2. PIN DEFINITIONS (EXACT USER HARDWARE MATCH)
// ======================================================================================

// ---------- IR SENSORS ----------
#define IR_L 32
#define IR_C 23  // Middle sensor for the perfect black tape
#define IR_R 22

// ---------- L293D / L298N MOTOR DRIVER ----------
#define L_IN1 14
#define L_IN2 27
#define L_EN  25

#define R_IN1 26
#define R_IN2 33
#define R_EN  13

// ---------- FRONT ULTRASONIC ----------
#define F_TRIG 18
#define F_ECHO 34

// ---------- REAR ULTRASONIC ----------
#define B_TRIG 19
#define B_ECHO 35

// ---------- MFRC522 RC522 RFID READER ----------
#define NFC_SS_PIN    5     // RC522 SDA / SS -> D5
#define NFC_RST_PIN   2     // RC522 RST      -> D2
#define NFC_SCK_PIN   15    // RC522 SCK      -> D15
#define NFC_MISO_PIN  16    // RC522 MISO     -> RX2
#define NFC_MOSI_PIN  17    // RC522 MOSI     -> TX2

// ======================================================================================
// 3. SETTINGS & MOTOR CALIBRATION (USER TESTED VALUES)
// ======================================================================================
#define ON_LINE           HIGH // 1 on Black Tape, 0 on White Floor
#define L_SPEED           170  // Reduced speed for faster left motor
#define R_SPEED           200  // Higher speed for slower right motor
#define TURN_SPEED        200  // Confident pivot turning
#define OBSTACLE_DISTANCE 15   // Safety brake threshold in cm

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
  // Fallbacks
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

bool robotRunning = false;
int activeGuestId = 0;
String activeGuestName = "NONE";
String activeCardUid = "NONE";
unsigned long lastNfcScanTime = 0;
unsigned long lastTelemetryTime = 0;

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
// 5. MOTOR CONTROL (USER-TESTED SPEEDS & INVERTED RIGHT MOTOR POLARITY)
// ======================================================================================
void setSpeed() {
  analogWrite(L_EN, L_SPEED);
  analogWrite(R_EN, R_SPEED);
}

void setTurnSpeed() {
  analogWrite(L_EN, TURN_SPEED);
  analogWrite(R_EN, TURN_SPEED);
}

// Stop both motors immediately
void stopMotors() {
  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, LOW);

  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, LOW);

  analogWrite(L_EN, 0);
  analogWrite(R_EN, 0);
}

void stopRobot() {
  stopMotors();
}

// Forward: Both wheels drive forward straight (Right motor polarity reversed)
void forward() {
  setSpeed();

  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);

  // Reversed right motor wiring
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Backward: Both wheels reverse safely
void backward() {
  setSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);

  // Reversed right motor wiring
  digitalWrite(R_IN1, HIGH);
  digitalWrite(R_IN2, LOW);
}

// Pivot Turn Right: Left forward, Right backward
void right() {
  setTurnSpeed();

  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);

  // Reversed right motor wiring: backward = HIGH, LOW
  digitalWrite(R_IN1, HIGH);
  digitalWrite(R_IN2, LOW);
}

// Pivot Turn Left: Left backward, Right forward
void left() {
  setTurnSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);

  // Reversed right motor wiring: forward = LOW, HIGH
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// ======================================================================================
// 6. ULTRASONIC DISTANCE
// ======================================================================================
int distanceCM(int trig, int echo) {
  digitalWrite(trig, LOW);
  delayMicroseconds(2);

  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  unsigned long duration = pulseIn(echo, HIGH, 12000);

  if (duration == 0) {
    return 999;  // No echo detected
  }

  return duration / 58;
}

// ======================================================================================
// 7. WI-FI TELEMETRY TO LOCAL RELAY BRIDGE & AI BRAIN
// ======================================================================================
void postTelemetry(const String& event, const String& extraJson = "") {
  if (WiFi.status() != WL_CONNECTED) return;

  int frontDist = distanceCM(F_TRIG, F_ECHO);
  int backDist  = distanceCM(B_TRIG, B_ECHO);

  bool L = digitalRead(IR_L) == ON_LINE;
  bool C = digitalRead(IR_C) == ON_LINE;
  bool R = digitalRead(IR_R) == ON_LINE;
  String irStr = String(L ? "1" : "0") + String(C ? "1" : "0") + String(R ? "1" : "0");

  String payload = "{\"token\":\"" + String(AURA_AUTH_TOKEN) +
                   "\",\"event\":\"" + event +
                   "\",\"state\":\"" + String(robotRunning ? "ESCORTING" : "IDLE") +
                   "\",\"dist\":" + String(frontDist) +
                   ",\"back_dist\":" + String(backDist) +
                   ",\"ir\":\"" + irStr + "\"" +
                   ",\"guest\":\"" + activeGuestName + "\"" +
                   extraJson + "}";

  HTTPClient http;
  http.begin(currentServerUrl + "/api/esp32/telemetry");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(350);
  int code = http.POST(payload);
  http.end();
}

// ======================================================================================
// 8. NFC CARD SCAN (START TRIGGER)
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

    postTelemetry("NFC_TAP", ",\"valid\":true,\"uid\":\"" + uidStr + "\",\"id\":" + String(activeGuestId) + ",\"name\":\"" + activeGuestName + "\"");
    return true;
  } else {
    Serial.printf(">>> [NFC UNKNOWN] Unregistered Card: %s\n", formattedUid.c_str());
    Serial.println("=======================================================\n");
    postTelemetry("NFC_TAP", ",\"valid\":false,\"uid\":\"" + uidStr + "\",\"reason\":\"UNREGISTERED\"");
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
  Serial.println("  AURA-EJUST LINE FOLLOWER & AI ESCORT (ESP32)");
  Serial.println("=======================================================");

  // Initialize IR Sensors
  pinMode(IR_L, INPUT);
  pinMode(IR_C, INPUT);
  pinMode(IR_R, INPUT);

  // Initialize Motors
  pinMode(L_IN1, OUTPUT);
  pinMode(L_IN2, OUTPUT);
  pinMode(L_EN, OUTPUT);

  pinMode(R_IN1, OUTPUT);
  pinMode(R_IN2, OUTPUT);
  pinMode(R_EN, OUTPUT);

  stopMotors();

  // Initialize Ultrasonics
  pinMode(F_TRIG, OUTPUT);
  pinMode(F_ECHO, INPUT);

  pinMode(B_TRIG, OUTPUT);
  pinMode(B_ECHO, INPUT);

  stopRobot();

  // Initialize NFC Reader
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
  Serial.println("\n--- HARDWARE SENSOR HEALTH CHECK ---");
  Serial.printf("  Front Ultrasonic (Trig %d, Echo %d) : %d cm\n", F_TRIG, F_ECHO, distanceCM(F_TRIG, F_ECHO));
  Serial.printf("  Back Ultrasonic  (Trig %d, Echo %d) : %d cm\n", B_TRIG, B_ECHO, distanceCM(B_TRIG, B_ECHO));
  Serial.printf("  IR Left   (Pin %d) : %d (%s)\n", IR_L, (digitalRead(IR_L) == ON_LINE), (digitalRead(IR_L) == ON_LINE) ? "TAPE (1)" : "OFF (0)");
  Serial.printf("  IR Center (Pin %d) : %d (%s)\n", IR_C, (digitalRead(IR_C) == ON_LINE), (digitalRead(IR_C) == ON_LINE) ? "TAPE (1)" : "OFF (0)");
  Serial.printf("  IR Right  (Pin %d) : %d (%s)\n", IR_R, (digitalRead(IR_R) == ON_LINE), (digitalRead(IR_R) == ON_LINE) ? "TAPE (1)" : "OFF (0)");
  Serial.printf("  NFC Reader (SDA %d): %s (Version: 0x%02X)\n", NFC_SS_PIN, (nfcVer == 0x00 || nfcVer == 0xFF) ? "OFFLINE" : "READY", nfcVer);
  Serial.println("------------------------------------\n");

  // Connect to Wi-Fi
  Serial.printf("[WI-FI] Connecting to SSID: %s\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
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
  Serial.println("  STANDBY: Scan VIP Card on Reader to Start Escort!");
  Serial.println("=======================================================\n");

  robotRunning = false;
}

// ======================================================================================
// 10. MAIN LOOP
// ======================================================================================
void loop() {
  unsigned long now = millis();

  // Maintain Wi-Fi Auto-Reconnection
  if (WiFi.status() != WL_CONNECTED) {
    static unsigned long lastReconnect = 0;
    if (now - lastReconnect > 5000) {
      lastReconnect = now;
      Serial.println("[WI-FI] Connection lost. Attempting auto-reconnect to hotspot...");
      WiFi.reconnect();
    }
  }

  // Stream Wi-Fi Telemetry every 400ms
  if (now - lastTelemetryTime >= 400) {
    lastTelemetryTime = now;
    postTelemetry("HEARTBEAT");
  }

  // Continuous Live Telemetry in Serial Monitor (Every 300ms)
  static unsigned long lastPrint = 0;
  if (now - lastPrint >= 300) {
    lastPrint = now;

    int fDist = distanceCM(F_TRIG, F_ECHO);
    int bDist = distanceCM(B_TRIG, B_ECHO);

    bool L = digitalRead(IR_L) == ON_LINE;
    bool C = digitalRead(IR_C) == ON_LINE;
    bool R = digitalRead(IR_R) == ON_LINE;

    byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    const char* nfcStatus = (v == 0x00 || v == 0xFF) ? "OFFLINE" : "READY";

    Serial.printf("[SENSORS] Front: %3d cm | Back: %3d cm | IR: [L:%d C:%d R:%d] | NFC: %-7s | Robot: %-7s | VIP: %s\n",
                  fDist, bDist,
                  L ? 1 : 0, C ? 1 : 0, R ? 1 : 0,
                  nfcStatus,
                  robotRunning ? "RUNNING" : "STANDBY",
                  activeGuestName.c_str());
  }

  // 1. NFC Scan Gate: Waits for VIP Card tap to start
  if (!robotRunning) {
    stopRobot();
    if (checkNfcTap()) {
      Serial.println("[START] Card verified! Starting line follower in 800ms...");
      delay(800);
      robotRunning = true;
      postTelemetry("STATUS", ",\"action\":\"ESCORTING\"");
    }
    delay(10);
    return;
  }

  // 2. Stop when an obstacle is detected in front
  if (distanceCM(F_TRIG, F_ECHO) < OBSTACLE_DISTANCE) {
    stopRobot();
    postTelemetry("OBSTACLE", ",\"dist\":" + String(distanceCM(F_TRIG, F_ECHO)));
    return;
  }

  // 3. Read IR sensors (1 = Black Tape, 0 = White Floor)
  bool L = digitalRead(IR_L) == ON_LINE;
  bool C = digitalRead(IR_C) == ON_LINE; // 1 in middle is responsible for the perfect line
  bool R = digitalRead(IR_R) == ON_LINE;

  // 4. Follow the line (User's Exact Verified Logic)
  if (!L && C && !R) {
    // Center sensor detects the line -> Cruise forward straight!
    forward();
  }
  else if ((L && !R && C) || (L && !R && !C)) {
    // Line is on the left -> Steer left
    left();
  }
  else if ((R && !L && C) || (R && !L && !C)) {
    // Line is on the right -> Steer right
    right();
  }
  else if (L && C && R) {
    // All sensors detect the line -> Reached destination marker! Stop and wait for next guest!
    stopMotors();
    Serial.println("\n[DESTINATION] Cross line detected (L & C & R)! Arrived at endpoint.");
    Serial.println("[STANDBY] Ready for next VIP guest card tap!\n");
    postTelemetry("ARRIVED", ",\"dest\":\"Destination Endpoint\"");
    robotRunning = false;
  }
  else if (!L && !C && !R) {
    // Line lost: reverse only if the rear is clear
    stopMotors();

    if (distanceCM(B_TRIG, B_ECHO) > OBSTACLE_DISTANCE) {
      backward();
      delay(250);
      stopMotors();
    }
  }
  else {
    // Other sensor combinations
    forward();
  }

  delay(10);
}
