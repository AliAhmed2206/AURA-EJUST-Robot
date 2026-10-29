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
#define IN1 14
#define IN2 27
#define L_EN  25

#define IN3 26
#define IN4 33
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
// 2. SETTINGS
// ======================================================================================
#define ON_LINE           LOW // 1 on Black Tape, 0 on White Floor
#define SPEED             170
#define TURN_SPEED        200
#define TIME_SPIN_90      1000 // Milliseconds to spin 90 degrees (adjust for floor/battery)
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
// 4. MOTOR CONTROL
// ======================================================================================
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
void setupPWM(int pin) {
  ledcAttach(pin, 1000, 8);
}
void motorPWM(int pin, int speed) {
  ledcWrite(pin, constrain(speed, 0, 255));
}
#else
void setupPWM(int pin) {
  int ch = (pin == L_EN) ? 0 : 1;
  ledcSetup(ch, 1000, 8);
  ledcAttachPin(pin, ch);
}
void motorPWM(int pin, int speed) {
  int ch = (pin == L_EN) ? 0 : 1;
  ledcWrite(ch, constrain(speed, 0, 255));
}
#endif

// Positive = forward, negative = reverse
void motor(int in1, int in2, int en, int speed) {
  speed = constrain(speed, -255, 255);

  digitalWrite(in1, speed > 0);
  digitalWrite(in2, speed < 0);

  motorPWM(en, abs(speed));
}

void forward() {
  motorPWM(L_EN, SPEED);
  motorPWM(R_EN, SPEED);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void backward() {
  motorPWM(L_EN, SPEED);
  motorPWM(R_EN, SPEED);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void left() {
  motorPWM(L_EN, TURN_SPEED);
  motorPWM(R_EN, TURN_SPEED);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void right() {
  motorPWM(L_EN, TURN_SPEED);
  motorPWM(R_EN, TURN_SPEED);

  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void stop() {
  motorPWM(L_EN, 0);
  motorPWM(R_EN, 0);

  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
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
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  setupPWM(L_EN);
  setupPWM(R_EN);

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
// 8. MAIN LOOP
// ======================================================================================
void loop() {
  // Continuous Live Telemetry in Serial Monitor (Every 300ms)
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

    Serial.printf("[SENSORS] Front: %3d cm | Back: %3d cm | IR: [L:%d C:%d R:%d] | NFC: %-7s | Robot: %-7s | VIP: %s\n",
                  fDist, bDist,
                  L ? 1 : 0, C ? 1 : 0, R ? 1 : 0,
                  nfcStatus,
                  robotRunning ? "RUNNING" : "STANDBY",
                  activeGuestName.c_str());
  }

  // 1. NFC Scan Gate: Waits for VIP Card tap to start
  if (!robotRunning) {
    stop();
    if (checkNfcTap()) {
      Serial.println("[START] Card verified! Delaying 2 seconds...");
      stop();
      delay(2000); // 1. Immediate 2-second delay after scanning

      Serial.println("[START] Turning 90 degrees...");
      // 2. Turn 90 degrees (Clockwise. If you need counter-clockwise, use: -TURN_SPEED, TURN_SPEED)
      unsigned long t0 = millis();
      left();
      while (millis() - t0 < TIME_SPIN_90) {
        // If center IR catches black tape during the turn, lock onto line immediately
        if (millis() - t0 > 300 && digitalRead(IR_C) == ON_LINE) {
          Serial.println("[LINE LOCKED] Center IR caught black tape during 90° turn!");
          break;
        }
        delay(10);
      }
      stop();
      delay(200);

      // 3. Normal line follower active until three IRs read 1s
      Serial.println("[START] Normal line follower active until three IRs read 1s (L & C & R)...");
      robotRunning = true;
    }
    delay(10);
    return;
  }


  // 2. Stop when an obstacle is detected in front
  if (distanceCM(F_TRIG, F_ECHO) < OBSTACLE_DISTANCE) {
    stop();
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
    stop();
    Serial.println("\n[DESTINATION] Cross line detected (L & C & R)! Arrived at endpoint.");
    Serial.println("[STANDBY] Ready for next VIP guest card tap!\n");
    robotRunning = false;
  }
  else if (!L && !C && !R) {
    // Line lost: reverse only if the rear is clear
    stop();
    if (distanceCM(B_TRIG, B_ECHO) > OBSTACLE_DISTANCE) {
      backward();
      delay(250);
      stop();
    }
  }
  else {
    // Other sensor combinations
    forward();
  }

  delay(10);
}