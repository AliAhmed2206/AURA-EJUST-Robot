#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESPmDNS.h>
#include <SPI.h>
#include <MFRC522.h>

// ======================================================================================
// 1. WI-FI & SERVER TELEMETRY CONFIGURATION
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

// Backward-compatibility aliases
#define IN1 L_IN1
#define IN2 L_IN2
#define IN3 R_IN1
#define IN4 R_IN2

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
// 3. SETTINGS & KINEMATICS (PROVEN PERFECT VALUES)
// ======================================================================================
#define ON_LINE           LOW  // 1 on Black Tape, 0 on White Floor (LOW = Detected)
#define L_SPEED           170  // Reduced speed for faster left motor
#define R_SPEED           150  // Higher speed for slower right motor
#define SPEED             200  // General forward reference
#define TURN_SPEED        200  // Turning speed
#define TIME_SPIN_90      1500 // Calibrate for the initial departure turn
#define TIME_SPIN_180     1890 // Estimated from 160-degree result at 1500 ms; calibrate on floor
#define TIME_PIVOT_90     1000 // Initial estimate: half the 180-degree pivot time
#define THEATRE_WAIT_MS   10000// Wait 10 seconds at the theatre
#define MARKER_CONFIRM_MS 50   // Require all three IR sensors on black briefly
#define OBSTACLE_DISTANCE 15   // Emergency stop distance in cm

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
  {"53D10572420001", "Marwan Yasser",  14},
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
bool firstDeparture = true;
bool markerArmed = false;
unsigned long markerCandidateSince = 0;
bool nextMarkerTurns = true; // Alternate: first marker = 180 turn, next marker = stop, repeat

enum TripState {
  GOING_TO_THEATRE,
  RETURNING_TO_START
};
TripState tripState = GOING_TO_THEATRE;
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
// 5. MOTOR CONTROL (Tested L298N + Right Motor Polarity Reversed)
// ======================================================================================

// Apply separate speeds to compensate for faster left motor
void setSpeed() {
  analogWrite(L_EN, L_SPEED);
  analogWrite(R_EN, R_SPEED);
}

// Apply turn speeds
void setTurnSpeed() {
  analogWrite(L_EN, TURN_SPEED);
  analogWrite(R_EN, TURN_SPEED);
}

// Stop both motors
void stopMotors() {
  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, LOW);

  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, LOW);

  analogWrite(L_EN, 0);
  analogWrite(R_EN, 0);
}

// Alias for stop()
void stop() {
  stopMotors();
}

void stopRobot() {
  stopMotors();
}

// Forward: both wheels drive forward straight
void forward() {
  setSpeed();

  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);

  // Reversed right motor: LOW / HIGH drives forward
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Backward: both wheels drive backward safely
void backward() {
  setSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);

  // Reversed right motor: HIGH / LOW drives backward
  digitalWrite(R_IN1, HIGH);
  digitalWrite(R_IN2, LOW);
}

// Turn right: Left wheel forward, Right wheel backward
void right() {
  setTurnSpeed();

  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);

  // Reversed right motor: HIGH / LOW drives backward
  digitalWrite(R_IN1, HIGH);
  digitalWrite(R_IN2, LOW);
}

// Turn left: Left wheel backward, Right wheel forward
void left() {
  setTurnSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);

  // Reversed right motor: LOW / HIGH drives forward
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Pivot in place 180 degrees: left wheel backward, right wheel forward.
void spin180() {
  setTurnSpeed();
  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Pivot left in place for approximately 90 degrees to lock onto line.
void spinLeft90InPlace() {
  setTurnSpeed();
  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
  delay(TIME_PIVOT_90);
  stopMotors();
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
// 7. WI-FI TELEMETRY TO LOCAL RELAY BRIDGE & AURA PHONE SCREEN
// ======================================================================================
void postTelemetry(const String& event, const String& extraJson = "") {
  if (WiFi.status() != WL_CONNECTED) return;

  int frontDist = distanceCM(F_TRIG, F_ECHO);
  int backDist  = distanceCM(B_TRIG, B_ECHO);

  bool L = digitalRead(IR_L) == ON_LINE;
  bool C = digitalRead(IR_C) == ON_LINE;
  bool R = digitalRead(IR_R) == ON_LINE;
  String irStr = String(L ? "1" : "0") + String(C ? "1" : "0") + String(R ? "1" : "0");

  String rState = robotRunning ? (tripState == GOING_TO_THEATRE ? "ESCORTING" : "RETURNING") : "STANDBY";

  String payload = "{\"token\":\"" + String(AURA_AUTH_TOKEN) +
                   "\",\"event\":\"" + event +
                   "\",\"state\":\"" + rState +
                   "\",\"dist\":" + String(frontDist) +
                   ",\"back_dist\":" + String(backDist) +
                   ",\"ir\":\"" + irStr + "\"" +
                   ",\"uid\":\"" + activeCardUid + "\"" +
                   ",\"guest\":\"" + activeGuestName + "\"" +
                   ",\"name\":\"" + activeGuestName + "\"" +
                   extraJson + "}";

  HTTPClient http;
  http.begin(currentServerUrl + "/api/esp32/telemetry");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(120); // Fast timeout so it never blocks motor loop
  http.POST(payload);
  http.end();
}

// ======================================================================================
// 8. NFC CARD SCAN (START TRIGGER)
// ======================================================================================
bool checkNfcTap() {
  if (!rfid.PICC_IsNewCardPresent()) return false;
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

    // Instantly notify AURA Phone WebApp so AI Face greets the guest by name!
    postTelemetry("NFC_TAP", ",\"valid\":true,\"id\":" + String(activeGuestId) + ",\"name\":\"" + activeGuestName + "\"");
    return true;
  } else {
    Serial.printf(">>> [NFC UNKNOWN] Unregistered Card: %s\n", formattedUid.c_str());
    Serial.println("=======================================================\n");
    postTelemetry("NFC_TAP", ",\"valid\":false,\"reason\":\"UNREGISTERED\"");
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
  Serial.println("  AURA-EJUST LINE FOLLOWER & VIP ESCORT (WI-FI EDITION)");
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

  stop();

  // Initialize Ultrasonics
  pinMode(F_TRIG, OUTPUT);
  pinMode(F_ECHO, INPUT);

  pinMode(B_TRIG, OUTPUT);
  pinMode(B_ECHO, INPUT);

  stop();

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

  // Connect to Wi-Fi Hotspot
  Serial.printf("[WI-FI] Connecting to SSID: %s\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.persistent(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 25) {
    delay(300);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[WI-FI] Connected successfully!");
    Serial.printf("[WI-FI] ESP32 IP Address: %s\n", WiFi.localIP().toString().c_str());

    if (MDNS.begin("aura-robot")) {
      IPAddress pcIP = MDNS.queryHost("Ali-Mohamed", 1500);
      if (pcIP != INADDR_NONE) {
        currentServerUrl = "http://" + pcIP.toString() + ":8080";
        Serial.printf("[mDNS] Found Laptop at %s!\n", currentServerUrl.c_str());
      }
    }
    Serial.printf("[WI-FI] Gateway Bridge: %s\n", currentServerUrl.c_str());
    postTelemetry("ONLINE", ",\"ip\":\"" + WiFi.localIP().toString() + "\"");
  } else {
    Serial.println("\n[WI-FI NOTICE] Wi-Fi not connected. Continuing autonomously offline...");
  }

  Serial.println("=======================================================");
  Serial.println("  STANDBY: Scan VIP Card on Reader to Start Escort!");
  Serial.println("=======================================================\n");

  robotRunning = false;
}

// ======================================================================================
// 10. MAIN LOOP: ALTERNATE ENDPOINT ACTIONS + LIVE STREAM TELEMETRY
// At every confirmed crossbar, alternate between a 180-degree turn and stopping for NFC.
// One continuous line is used in both directions.
// ======================================================================================
void loop() {
  unsigned long now = millis();

  // Non-blocking Wi-Fi auto-reconnect check (every 5 seconds)
  static unsigned long lastWifiCheck = 0;
  if (now - lastWifiCheck > 5000) {
    lastWifiCheck = now;
    if (WiFi.status() != WL_CONNECTED) {
      WiFi.reconnect();
    }
  }

  // Stream Live Telemetry to AURA Phone Screen & Serial Monitor (every 300 ms)
  static unsigned long lastTelemetry = 0;
  if (now - lastTelemetry >= 300) {
    lastTelemetry = now;

    int fDist = distanceCM(F_TRIG, F_ECHO);
    int bDist = distanceCM(B_TRIG, B_ECHO);
    bool L = digitalRead(IR_L) == ON_LINE;
    bool C = digitalRead(IR_C) == ON_LINE;
    bool R = digitalRead(IR_R) == ON_LINE;
    byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    const char* nfcStatus = (v == 0x00 || v == 0xFF) ? "OFFLINE" : "READY";

    Serial.printf("[SENSORS] Front:%3d cm | Back:%3d cm | IR:[L:%d C:%d R:%d] | NFC:%-7s | Robot:%-7s | VIP:%s\n",
                  fDist, bDist, L ? 1 : 0, C ? 1 : 0, R ? 1 : 0,
                  nfcStatus, robotRunning ? "RUNNING" : "STANDBY", activeGuestName.c_str());

    // Send HTTP JSON packet to Laptop Bridge -> Phone Screen HUD
    postTelemetry("HEARTBEAT");
  }

  // At the entrance, wait for a valid card. After each completed return trip,
  // the robot pivots left 90 degrees before entering standby.
  if (!robotRunning) {
    stop();
    if (checkNfcTap()) {
      Serial.printf("[START] VIP %s verified. Starting trip.\n", activeGuestName.c_str());
      delay(1500);

      if (firstDeparture) {
        if (digitalRead(IR_C) == ON_LINE) {
          Serial.println("[START] Robot already positioned on the black line! Proceeding directly...");
        } else {
          // Initial departure turn to lock onto the line if starting from greeting pose
          Serial.println("[START] Initial departure turn to lock onto black line...");
          unsigned long t0 = millis();
          left();
          while (millis() - t0 < TIME_SPIN_90) {
            if (millis() - t0 > 200 && digitalRead(IR_C) == ON_LINE) break;
            delay(10);
          }
          stop();
          delay(250);
        }
        firstDeparture = false;
      } else {
        // On the second and every later departure, pivot left 90 degrees
        // immediately after the valid NFC scan and before line-following starts.
        Serial.println("[START] Second/subsequent cycle: pivoting left 90 degrees before departure...");
        spinLeft90InPlace();
        delay(250);
      }

      // The first crossbar reached while moving is the theatre: turn around there.
      // The next crossbar is the start: stop and wait for the next guest.
      nextMarkerTurns = true;
      tripState = GOING_TO_THEATRE;
      markerArmed = false;
      markerCandidateSince = 0;
      robotRunning = true;
      Serial.println("[RUNNING] Following line; endpoint actions will alternate TURN, STOP, TURN, STOP...");
      postTelemetry("STATUS", ",\"action\":\"ESCORTING\"");
    }
    delay(10);
    return;
  }

  // Safety stop for a nearby obstacle. Trip remains active and resumes when clear.
  if (distanceCM(F_TRIG, F_ECHO) < OBSTACLE_DISTANCE) {
    stop();
    postTelemetry("OBSTACLE");
    return;
  }

  bool L = digitalRead(IR_L) == ON_LINE;
  bool C = digitalRead(IR_C) == ON_LINE;
  bool R = digitalRead(IR_R) == ON_LINE;
  bool allBlack = L && C && R;

  // Lockout after startup/turning: move clear of the same crossbar before re-arming.
  if (!markerArmed) {
    if (!allBlack) {
      markerArmed = true;
      markerCandidateSince = 0;
    } else {
      forward();
      delay(10);
      return;
    }
  }

  // Confirm all three sensors on black long enough to avoid reacting to a brief reading.
  if (allBlack) {
    if (markerCandidateSince == 0) markerCandidateSince = millis();

    if (millis() - markerCandidateSince >= MARKER_CONFIRM_MS) {
      markerCandidateSince = 0;
      stop();

      if (nextMarkerTurns) {
        Serial.println("[ENDPOINT] Crossbar detected. Pivoting 180 degrees...");
        postTelemetry("ARRIVED", ",\"dest\":\"Theatre Endpoint\"");
        spin180();
        delay(TIME_SPIN_180);
        stop();
        delay(250);

        // Alternate the next confirmed crossbar to STOP.
        nextMarkerTurns = false;
        tripState = (tripState == GOING_TO_THEATRE) ? RETURNING_TO_START : GOING_TO_THEATRE;
        markerArmed = false; // Prevent re-triggering on the same crossbar after pivoting.
        Serial.println("[TURN COMPLETE] Continuing along the same line in the opposite direction.");
        postTelemetry("STATUS", ",\"action\":\"RETURNING\"");
      } else {
        Serial.println("[ENDPOINT] Entrance crossbar detected. Pivoting left 90 degrees before standby...");
        stop();
        delay(250);
        spinLeft90InPlace();  // 90-degree left turn at the end of the return phase
        delay(250);

        // Enter standby only after completing the endpoint 90-degree turn.
        robotRunning = false;
        nextMarkerTurns = true; // Next trip's theatre endpoint will pivot 180 degrees.
        markerArmed = false;
        Serial.println("[STANDBY] Startpoint reached; 90-degree left turn complete. Scan a registered card to begin the next departure.\n");
        postTelemetry("ARRIVED", ",\"dest\":\"Entrance Startpoint\"");
      }
      return;
    }

    // Creep forward while confirming the marker.
    forward();
    delay(10);
    return;
  } else {
    markerCandidateSince = 0;
  }

  // Normal three-sensor line following.
  if (!L && C && !R) {
    forward();
  } else if (L && !R) {
    left();
  } else if (R && !L) {
    right();
  } else if (!L && !C && !R) {
    stop(); // Lost line: do not drive blindly.
  } else {
    forward();
  }

  delay(10);
}
