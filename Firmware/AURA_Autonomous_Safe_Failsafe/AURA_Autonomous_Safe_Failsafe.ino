/*
 * ======================================================================================
 * AURA-EJUST HUMANOID ROBOT - AUTONOMOUS SAFE FAILSAFE FIRMWARE (v3.5)
 * ======================================================================================
 * 100% STANDALONE EMERGENCY & BACKUP CODE - ZERO AI / ZERO WI-FI DEPENDENCY
 * 
 * Hardware Architecture:
 *   1. ESP32-WROOM-32 DevKit V1
 *   2. Dual L298N Differential Motor Drivers (4x 12V DC Motors)
 *   3. 3x TCRT5000 Infrared Sensors (Left, Center, Right Line Tracking)
 *   4. Front Ultrasonic Sensor HC-SR04 (Autonomous Emergency Brake < 15cm)
 *   5. Rear Ultrasonic Sensor HC-SR04 (Back Obstacle Detection)
 *   6. MFRC522 RFID Card Reader (VIP Guest Escort Activation)
 *   7. Onboard LED (Pin 2) - Realtime status indicator
 * 
 * Operation Mode:
 *   - Boots instantly in IDLE state.
 *   - Swipe any VIP RFID card OR wave hand within 8cm of Front Ultrasonic to START.
 *   - Autonomously tracks line at calibrated cruising speed (PWM 170).
 *   - Automatically slows & turns at curves (PWM 200).
 *   - Instantly halts if front obstacle detected (< 15cm), resumes when clear.
 *   - Counts station markers (cross-lines) and halts cleanly upon arrival at Station 1.
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>

// ---------- 1. HARDWARE PIN DEFINITIONS ----------

// TCRT5000 IR Line Tracking Sensors
#define IR_L 32
#define IR_C 23
#define IR_R 22

// L298N Motor Driver Pins
#define L_IN1 14
#define L_IN2 27
#define L_EN  25

#define R_IN1 26
#define R_IN2 33
#define R_EN  13

// Ultrasonic Distance Sensors
#define F_TRIG 19
#define F_ECHO 35

#define B_TRIG 18
#define B_ECHO 34

// MFRC522 RFID Reader (Hardware SPI)
#define NFC_SS_PIN   5
#define NFC_RST_PIN  21

// Built-in Status LED
#define STATUS_LED   2

// ---------- 2. TUNED ROBOT PARAMETERS ----------
#define ON_LINE           LOW   // LOW when sensor detects black line
#define SPEED             170   // Normal cruising PWM (0-255)
#define TURN_SPEED        200   // Turning adjustment PWM
#define OBSTACLE_DISTANCE 15    // Emergency stop threshold (cm)
#define RESUME_DISTANCE   22    // Path clear resume threshold (cm)

// Robot State Machine
enum RobotState {
    STATE_IDLE,        // Waiting for guest trigger (RFID swipe or wave gesture)
    STATE_ESCORTING,   // Actively following line toward destination
    STATE_OBSTACLE,    // Temporarily halted by obstacle in front
    STATE_ARRIVED      // Successfully reached destination marker
};

RobotState currentState = STATE_IDLE;
uint8_t markersCount = 0;
uint8_t targetMarkers = 1;     // Stop at 1st marker station (Grand Theatre)
unsigned long lastMarkerTime = 0;
unsigned long lastTelemetryPrint = 0;

MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);

// ---------- 3. MOTOR & PWM DRIVER ----------
#if ESP_ARDUINO_VERSION_MAJOR >= 3
void setupPWM(int pin, int ch) {
    ledcAttach(pin, 1000, 8);
}
void motorPWM(int pin, int ch, int speed) {
    ledcWrite(pin, speed);
}
#else
void setupPWM(int pin, int ch) {
    ledcSetup(ch, 1000, 8);
    ledcAttachPin(pin, ch);
}
void motorPWM(int pin, int ch, int speed) {
    ledcWrite(ch, speed);
}
#endif

void motor(int in1, int in2, int enPin, int ch, int speed) {
    speed = constrain(speed, -255, 255);
    digitalWrite(in1, speed > 0 ? HIGH : LOW);
    digitalWrite(in2, speed < 0 ? HIGH : LOW);
    motorPWM(enPin, ch, abs(speed));
}

void moveRobot(int left, int right) {
    motor(L_IN1, L_IN2, L_EN, 0, left);
    motor(R_IN1, R_IN2, R_EN, 1, right);
}

void stopRobot() {
    moveRobot(0, 0);
}

// ---------- 4. ULTRASONIC SENSOR READING ----------
int readDistance(int trigPin, int echoPin) {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 28000); // Max ~4.8 meters
    if (duration == 0) return 999;
    return (int)(duration * 0.034 / 2);
}

// ---------- 5. AUTONOMOUS LINE FOLLOWING LOGIC ----------
void stepAutonomousEscort() {
    int frontDist = readDistance(F_TRIG, F_ECHO);

    // Obstacle Safety Brake
    if (frontDist < OBSTACLE_DISTANCE) {
        stopRobot();
        currentState = STATE_OBSTACLE;
        Serial.printf("[SAFETY BRAKE] Obstacle at %d cm! Halted.\n", frontDist);
        digitalWrite(STATUS_LED, LOW);
        return;
    }

    // Read 3 IR Sensors
    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE);
    bool R = (digitalRead(IR_R) == ON_LINE);

    unsigned long now = millis();

    // Check for Station Cross-Line Marker (All 3 detect black line)
    if (L && C && R) {
        if (now - lastMarkerTime > 800) { // 800ms debounce
            markersCount++;
            lastMarkerTime = now;
            Serial.printf("[STATION] Cross-Line Marker Detected! Count: %d / %d\n", markersCount, targetMarkers);
            
            if (markersCount >= targetMarkers) {
                stopRobot();
                currentState = STATE_ARRIVED;
                Serial.println("[MISSION COMPLETE] Arrived at destination station. Standing by.");
                for (int i = 0; i < 4; i++) {
                    digitalWrite(STATUS_LED, HIGH); delay(100);
                    digitalWrite(STATUS_LED, LOW); delay(100);
                }
                return;
            }
        }
        // Roll forward steadily through the marker
        moveRobot(SPEED, SPEED);
        return;
    }

    // Proportional Navigation Guidance
    if (C && !L && !R) {
        // Centered on track -> Full Cruise
        moveRobot(SPEED, SPEED);
    } else if (L && !R) {
        // Veering right -> Steer hard left
        moveRobot(0, TURN_SPEED);
    } else if (R && !L) {
        // Veering left -> Steer hard right
        moveRobot(TURN_SPEED, 0);
    } else if (L && C) {
        // Gentle left correction
        moveRobot(SPEED / 2, TURN_SPEED);
    } else if (R && C) {
        // Gentle right correction
        moveRobot(TURN_SPEED, SPEED / 2);
    } else {
        // Off track / lost line -> Creep forward slowly to recover
        moveRobot(SPEED / 2, SPEED / 2);
    }
}

// ---------- 6. RFID VIP GUEST TRIGGER ----------
void checkRfidTrigger() {
    if (!rfid.PICC_IsNewCardPresent()) return;
    if (!rfid.PICC_ReadCardSerial()) return;

    String uidStr = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) uidStr += "0";
        uidStr += String(rfid.uid.uidByte[i], HEX);
    }
    uidStr.toUpperCase();

    Serial.printf("[RFID] VIP Card Detected: %s\n", uidStr.c_str());
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    // Start Autonomous Escort
    markersCount = 0;
    currentState = STATE_ESCORTING;
    Serial.println("[START] Autonomous Escort Initiated by VIP Card!");
    digitalWrite(STATUS_LED, HIGH);
}

// ---------- 7. GESTURE AUTO-START TRIGGER ----------
void checkGestureTrigger() {
    int dist = readDistance(F_TRIG, F_ECHO);
    if (dist > 2 && dist < 8) { // Hand held close to front sensor
        delay(300);
        int confirmDist = readDistance(F_TRIG, F_ECHO);
        if (confirmDist > 2 && confirmDist < 8) {
            markersCount = 0;
            currentState = STATE_ESCORTING;
            Serial.println("[START] Autonomous Escort Initiated by Hand Wave Gesture!");
            digitalWrite(STATUS_LED, HIGH);
            delay(500);
        }
    }
}

// ---------- 8. SETUP & INITIALIZATION ----------
void setup() {
    Serial.begin(115200);
    delay(200);

    Serial.println("\n=======================================================");
    Serial.println("  AURA-EJUST - STANDALONE FAILSAFE AUTONOMOUS FIRMWARE ");
    Serial.println("  100% Local Hardware Control | Zero AI Dependency     ");
    Serial.println("=======================================================");

    // Pin Modes
    pinMode(IR_L, INPUT);
    pinMode(IR_C, INPUT);
    pinMode(IR_R, INPUT);

    pinMode(L_IN1, OUTPUT);
    pinMode(L_IN2, OUTPUT);
    pinMode(R_IN1, OUTPUT);
    pinMode(R_IN2, OUTPUT);

    pinMode(F_TRIG, OUTPUT);
    pinMode(F_ECHO, INPUT);
    pinMode(B_TRIG, OUTPUT);
    pinMode(B_ECHO, INPUT);

    pinMode(STATUS_LED, OUTPUT);
    digitalWrite(STATUS_LED, LOW);

    // Motor PWM
    setupPWM(L_EN, 0);
    setupPWM(R_EN, 1);
    stopRobot();

    // SPI & RFID
    SPI.begin();
    rfid.PCD_Init();
    Serial.println("[INIT] Motors, Ultrasonic, IR Sensors & RFID Initialized.");
    Serial.println("[STANDBY] Swipe VIP Card OR wave hand within 8cm to begin escort.");

    // Flash LED 3 times on boot
    for (int i = 0; i < 3; i++) {
        digitalWrite(STATUS_LED, HIGH); delay(80);
        digitalWrite(STATUS_LED, LOW); delay(80);
    }
}

// ---------- 9. MAIN AUTONOMOUS LOOP ----------
void loop() {
    unsigned long now = millis();

    switch (currentState) {
        case STATE_IDLE:
            stopRobot();
            checkRfidTrigger();
            checkGestureTrigger();
            break;

        case STATE_ESCORTING:
            digitalWrite(STATUS_LED, (now / 250) % 2 == 0); // Blink while escorting
            stepAutonomousEscort();
            break;

        case STATE_OBSTACLE: {
            stopRobot();
            int frontDist = readDistance(F_TRIG, F_ECHO);
            if (frontDist >= RESUME_DISTANCE) {
                Serial.printf("[RESUME] Path Clear (%d cm)! Resuming Escort.\n", frontDist);
                currentState = STATE_ESCORTING;
            }
            break;
        }

        case STATE_ARRIVED:
            stopRobot();
            digitalWrite(STATUS_LED, HIGH);
            // Standby for next guest (swipe card to escort again)
            checkRfidTrigger();
            checkGestureTrigger();
            break;
    }

    // Periodic Telemetry to Serial Monitor (Every 500ms)
    if (now - lastTelemetryPrint > 500) {
        lastTelemetryPrint = now;
        int fDist = readDistance(F_TRIG, F_ECHO);
        int bDist = readDistance(B_TRIG, B_ECHO);
        bool L = (digitalRead(IR_L) == ON_LINE);
        bool C = (digitalRead(IR_C) == ON_LINE);
        bool R = (digitalRead(IR_R) == ON_LINE);
        Serial.printf("[TELEMETRY] State: %d | Front: %d cm | Back: %d cm | IR: [%d %d %d] | Markers: %d\n",
            currentState, fDist, bDist, L ? 1 : 0, C ? 1 : 0, R ? 1 : 0, markersCount);
    }

    delay(20); // 50 Hz control loop
}
