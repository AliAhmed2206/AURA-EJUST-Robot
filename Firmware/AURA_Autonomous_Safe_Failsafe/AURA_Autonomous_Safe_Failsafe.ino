#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>

// ======================================================================================
// 1. PIN DEFINITIONS (EXACT USER HARDWARE MATCH)
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
// 2. SETTINGS
// ======================================================================================
#define ON_LINE           LOW // 1 on Black Tape, 0 on White Floor
#define L_SPEED           170 // Reduced speed for faster left motor
#define R_SPEED           150 // Higher speed for slower right motor
#define SPEED             170 // General forward reference
#define TURN_SPEED        200 // Turning speed
#define TIME_SPIN_90      1500 // Calibrate for the initial departure turn
#define TIME_SPIN_180     1500 // CALIBRATE: actual 180-degree pivot turn time
#define THEATRE_WAIT_MS   10000 // Wait 10 seconds at the theatre
#define MARKER_CONFIRM_MS 50   // Require all three IR sensors on black briefly
#define OBSTACLE_DISTANCE 15

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

enum TripState {
  GOING_TO_THEATRE,
  WAITING_AT_THEATRE,
  RETURNING_TO_START
};
TripState tripState = GOING_TO_THEATRE;
int activeGuestId = 0;
String activeGuestName = "NONE";
unsigned long lastNfcScanTime = 0;

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
// 4. MOTOR CONTROL (Tested L298N + Right Motor Polarity Reversed)
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

// Forward: both wheels drive forward
void forward() {
  setSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);

  // Reversed right motor (LOW / HIGH drives forward)
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Backward: both wheels drive backward
void backward() {
  setSpeed();

  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);

  // Reversed right motor (HIGH / LOW drives backward)
  digitalWrite(R_IN1, HIGH);
  digitalWrite(R_IN2, LOW);
}

// Turn right: Left wheel forward, Right wheel backward
void right() {
  setTurnSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, HIGH);

  // Reversed right motor (HIGH / LOW drives backward)
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, LOW);
}

// Turn left: Left wheel backward, Right wheel forward
void left() {
  setTurnSpeed();

  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, LOW);

  // Reversed right motor (LOW / HIGH drives forward)
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Pivot in place: left wheel backward, right wheel forward.
// Calibrate TIME_SPIN_180 on the actual robot and floor.
void spin180() {
  setTurnSpeed();
  digitalWrite(L_IN1, HIGH);
  digitalWrite(L_IN2, LOW);
  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, HIGH);
}

// Stop both motors
void stop() {
  digitalWrite(L_IN1, LOW);
  digitalWrite(L_IN2, LOW);

  digitalWrite(R_IN1, LOW);
  digitalWrite(R_IN2, LOW);

  analogWrite(L_EN, 0);
  analogWrite(R_EN, 0);
}

// ======================================================================================
// 5. ULTRASONIC DISTANCE
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
// 6. NFC CARD SCAN (START TRIGGER)
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
    return true;
  } else {
    Serial.printf(">>> [NFC UNKNOWN] Unregistered Card: %s\n", formattedUid.c_str());
    Serial.println("=======================================================\n");
    return false;
  }
}

// ======================================================================================
// 7. SETUP
// ======================================================================================
void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("\n=======================================================");
  Serial.println("  AURA-EJUST LINE FOLLOWER & VIP NFC ESCORT ROBOT");
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

  Serial.println("=======================================================");
  Serial.println("  STANDBY: Scan VIP Card on Reader to Start Escort!");
  Serial.println("=======================================================\n");

  robotRunning = false;
}

// ======================================================================================
// 8. MAIN LOOP: OUTBOUND -> THEATRE WAIT -> 180-DEGREE TURN -> RETURN
// Track: one continuous black line, with a perpendicular black crossbar at each endpoint.
// Endpoint marker = all three line sensors detect black at the same time.
// ======================================================================================
void loop() {
  // Live sensor telemetry (every 300 ms)
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint >= 300) {
    lastPrint = millis();
    int fDist = distanceCM(F_TRIG, F_ECHO);
    int bDist = distanceCM(B_TRIG, B_ECHO);
    bool L = digitalRead(IR_L) == ON_LINE;
    bool C = digitalRead(IR_C) == ON_LINE;
    bool R = digitalRead(IR_R) == ON_LINE;
    byte v = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    const char* nfcStatus = (v == 0x00 || v == 0xFF) ? "OFFLINE" : "READY";
    const char* stateName = !robotRunning ? "STANDBY" :
      (tripState == GOING_TO_THEATRE ? "OUTBOUND" :
       tripState == WAITING_AT_THEATRE ? "THEATRE_WAIT" : "RETURNING");
    Serial.printf("[SENSORS] Front:%3d cm | Back:%3d cm | IR:[L:%d C:%d R:%d] | NFC:%-7s | State:%-12s | VIP:%s\n",
                  fDist, bDist, L ? 1 : 0, C ? 1 : 0, R ? 1 : 0,
                  nfcStatus, stateName, activeGuestName.c_str());
  }

  // At the entrance, wait for a registered guest card.
  if (!robotRunning) {
    stop();
    if (checkNfcTap()) {
      Serial.printf("[START] VIP %s verified. Starting trip.\n", activeGuestName.c_str());
      delay(2000);

      // Keep the original initial 90-degree departure turn only for the first trip.
      // After returning, the robot is already aligned with the same line.
      if (firstDeparture) {
        Serial.println("[START] Initial departure turn...");
        unsigned long t0 = millis();
        left();
        while (millis() - t0 < TIME_SPIN_90) {
          if (millis() - t0 > 300 && digitalRead(IR_C) == ON_LINE) break;
          delay(10);
        }
        stop();
        delay(200);
        firstDeparture = false;
      }

      tripState = GOING_TO_THEATRE;
      markerArmed = false; // Ignore the start crossbar until the robot has cleared it.
      markerCandidateSince = 0;
      robotRunning = true;
      Serial.println("[OUTBOUND] Following line to theatre...");
    }
    delay(10);
    return;
  }

  // Safety stop for a nearby obstacle. The trip state is retained so it can resume.
  if (distanceCM(F_TRIG, F_ECHO) < OBSTACLE_DISTANCE) {
    stop();
    return;
  }

  bool L = digitalRead(IR_L) == ON_LINE;
  bool C = digitalRead(IR_C) == ON_LINE;
  bool R = digitalRead(IR_R) == ON_LINE;
  bool allBlack = L && C && R;

  // At the theatre: stop for guests, then turn around and return on the same line.
  if (tripState == WAITING_AT_THEATRE) {
    stop();
    Serial.println("[THEATRE] Arrived. Waiting for guests to exit...");
    delay(THEATRE_WAIT_MS);

    Serial.println("[RETURN] Pivoting approximately 180 degrees...");
    spin180();
    delay(TIME_SPIN_180);
    stop();
    delay(250);

    tripState = RETURNING_TO_START;
    markerArmed = false; // Ignore the theatre crossbar until sensors clear it.
    markerCandidateSince = 0;
    Serial.println("[RETURN] Following the same line back to the entrance...");
    return;
  }

  // Marker lockout: after starting or turning around, move off the crossbar before
  // allowing another endpoint marker to be recognized.
  if (!markerArmed) {
    if (!allBlack) {
      markerArmed = true;
      markerCandidateSince = 0;
    } else {
      // Move forward off the crossbar; do not treat it as the next endpoint.
      forward();
      delay(10);
      return;
    }
  }

  // Confirm a crossbar for MARKER_CONFIRM_MS to reduce false detections.
  if (allBlack) {
    if (markerCandidateSince == 0) markerCandidateSince = millis();
    if (millis() - markerCandidateSince >= MARKER_CONFIRM_MS) {
      stop();
      markerCandidateSince = 0;

      if (tripState == GOING_TO_THEATRE) {
        Serial.println("[THEATRE] Crossbar detected. Stopping at theatre.");
        tripState = WAITING_AT_THEATRE;
      } else if (tripState == RETURNING_TO_START) {
        Serial.println("[START] Entrance crossbar detected. Trip complete.");
        // Face the theatre again so the next guest's trip can use the same line.
        Serial.println("[START] Turning 180 degrees to face the theatre for the next trip...");
        spin180();
        delay(TIME_SPIN_180);
        stop();
        Serial.println("[STANDBY] Ready for the next registered guest card.\n");
        robotRunning = false;
        markerArmed = false;
      }
      return;
    }
    // Keep moving very slowly while confirming the marker.
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
    // Line lost: stop rather than driving blindly off the route.
    stop();
  } else {
    forward();
  }

  delay(10);
}
 