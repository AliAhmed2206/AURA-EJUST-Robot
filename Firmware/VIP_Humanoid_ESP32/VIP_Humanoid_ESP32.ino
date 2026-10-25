/*
 * ======================================================================================
 * AURA-EJUST — SIMPLIFIED RECEPTION & ESCORT FIRMWARE (ESP32 DevKit V1)
 * ======================================================================================
 * Hardware Components:
 *   1. ESP32-WROOM-32 DevKit V1
 *   2. MFRC522 NFC Reader (SPI) — 13.56 MHz (Supports 7-byte & 4-byte VIP Cards)
 *   3. L298N Motor Driver + 4x 12V DC Motors (Differential Drive: 2 Left, 2 Right)
 *   4. 1 or 2 TCRT5000 IR Sensors (Line Tracking / Destination Station Markers)
 *   5. 1 or 2 HC-SR04 Ultrasonic Sensors (Front Obstacle Collision Safety)
 *   6. Web Bluetooth (BLE Nordic UART Service) -> Direct Phone Screen Link (Zero Internet Needed)
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <MFRC522.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>

// ======================================================================================
// 1. PIN DEFINITIONS (ESP32 DevKit V1)
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

// ======================================================================================
// 2. BLE NORDIC UART SERVICE DEFINITIONS
// ======================================================================================
#define SERVICE_UUID           "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
#define CHARACTERISTIC_UUID_RX "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
#define CHARACTERISTIC_UUID_TX "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

BLEServer* pServer = NULL;
BLECharacteristic* pTxCharacteristic = NULL;
BLECharacteristic* pRxCharacteristic = NULL;
bool deviceConnected = false;
bool oldDeviceConnected = false;

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
unsigned long lastTelemetryTime = 0;
unsigned long lastNfcScanTime = 0;

// Manual Timed Movement State (Directional Voice & BLE Driving)
unsigned long manualDriveEndTime = 0;
bool manualDriveActive = false;
int curManualLeftSpeed = 0;
int curManualRightSpeed = 0;

// Object Instances
MFRC522 rfid(NFC_SS_PIN, NFC_RST_PIN);

// Forward Declarations
void setMotors(int leftSpeed, int rightSpeed);
void stopMotors();
void executeManualDrive(int leftSpeed, int rightSpeed, unsigned long durationMs);
void sendBlePacket(const String& json);
void handleIncomingCommand(const String& cmd);
long readUltrasonicCM(int trigPin, int echoPin);
long getMinObstacleDistance();

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
            sendBlePacket("{\"event\":\"OBSTACLE\",\"dist\":" + String(dist) + "}");
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
            sendBlePacket("{\"event\":\"OBSTACLE\",\"dist\":" + String(dist) + "}");
        }
        return;
    } else if (obstacleDetected) {
        obstacleDetected = false;
        Serial.printf("[CLEAR] Path Clear (%ld cm) — Resuming Escort\n", dist);
        sendBlePacket("{\"event\":\"CLEAR\",\"dist\":" + String(dist) + "}");
    }

    // 2. Read IR Sensor(s)
    int leftIR = digitalRead(IR_LEFT_PIN);
    int rightIR = (IR_RIGHT_PIN >= 0) ? digitalRead(IR_RIGHT_PIN) : -1;

    // A. Single IR Sensor Mode (Acts as station/checkpoint marker reader)
    if (rightIR == -1) {
        if (leftIR == LINE_ACTIVE) {
            markersCount++;
            Serial.printf("[MARKER] Station Crossed: %d / %d\n", markersCount, targetMarkers);
            sendBlePacket("{\"event\":\"MARKER\",\"passed\":" + String(markersCount) + ",\"target\":" + String(targetMarkers) + "}");
            if (markersCount >= targetMarkers) {
                stopMotors();
                currentState = STATE_ARRIVED;
                sendBlePacket("{\"event\":\"ARRIVED\"}");
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
        sendBlePacket("{\"event\":\"MARKER\",\"passed\":" + String(markersCount) + ",\"target\":" + String(targetMarkers) + "}");
        if (markersCount >= targetMarkers) {
            stopMotors();
            currentState = STATE_ARRIVED;
            sendBlePacket("{\"event\":\"ARRIVED\"}");
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
        sendBlePacket("{\"event\":\"NFC_TAP\",\"valid\":false,\"uid\":\"READ_ERROR\",\"reason\":\"READ_ERROR\"}");
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
        // VALID VIP CARD (Numbered: VIP Guest 1 .. 21, no assigned destination)
        int guestId = VIP_CARDS[matchedIdx].id;
        activeGuestName = "VIP Guest " + String(guestId);
        markersCount = 0;

        Serial.printf("[NFC VALID] Welcome VIP Guest %d (Card: %s)\n", guestId, uidStr.c_str());

        String json = "{\"event\":\"NFC_TAP\",\"valid\":true,\"uid\":\"" + uidStr +
                      "\",\"id\":" + String(guestId) +
                      ",\"name\":\"" + activeGuestName + "\"}";
        sendBlePacket(json);

        // Start Escorting after brief welcome pause
        delay(1200);
        currentState = STATE_ESCORTING;
    } else {
        // UNREGISTERED / INVALID CARD
        Serial.printf("[NFC INVALID] Unknown Card Code: %s\n", uidStr.c_str());
        String json = "{\"event\":\"NFC_TAP\",\"valid\":false,\"uid\":\"" + uidStr + "\",\"reason\":\"UNREGISTERED\"}";
        sendBlePacket(json);
        // Do NOT start motors on invalid card!
    }
}

// ======================================================================================
// 9. BLE SERVER CALLBACKS & COMMAND PARSER
// ======================================================================================
class ServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
        deviceConnected = true;
        Serial.println("[BLE] Phone Connected!");
    }
    void onDisconnect(BLEServer* pServer) {
        deviceConnected = false;
        Serial.println("[BLE] Device Disconnected. Restarting advertising...");
        pServer->startAdvertising(); // Critical: ESP32 stops advertising upon disconnect unless restarted!
    }
};

String bleRxBuffer = "";
class RxCallbacks : public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
        String rx = pCharacteristic->getValue().c_str();
        if (rx.length() > 0) {
            bleRxBuffer += rx;
            while (bleRxBuffer.indexOf('\n') >= 0) {
                int idx = bleRxBuffer.indexOf('\n');
                String line = bleRxBuffer.substring(0, idx);
                bleRxBuffer = bleRxBuffer.substring(idx + 1);
                line.trim();
                if (line.length() > 0) handleIncomingCommand(line);
            }
        }
    }
};

void sendBlePacket(const String& json) {
    if (deviceConnected && pTxCharacteristic != NULL) {
        String packet = json + "\n";
        int len = packet.length();
        int offset = 0;
        while (offset < len) {
            int chunkLen = min(20, len - offset);
            pTxCharacteristic->setValue((uint8_t*)(packet.c_str() + offset), chunkLen);
            pTxCharacteristic->notify();
            offset += chunkLen;
            delay(10);
        }
    }
}

void handleIncomingCommand(const String& cmd) {
    Serial.print("[BLE RX] ");
    Serial.println(cmd);

    if (cmd.indexOf("START_ESCORT") >= 0) {
        markersCount = 0;
        currentState = STATE_ESCORTING;
        Serial.println("[CMD] Escort Started via Command");
        sendBlePacket("{\"event\":\"STATUS\",\"state\":\"ESCORTING\"}");
    } else if (cmd.indexOf("PAUSE") >= 0) {
        stopMotors();
        currentState = STATE_PAUSED;
        Serial.println("[CMD] Escort Paused");
        sendBlePacket("{\"event\":\"STATUS\",\"state\":\"PAUSED\"}");
    } else if (cmd.indexOf("RESUME") >= 0) {
        currentState = STATE_ESCORTING;
        Serial.println("[CMD] Escort Resumed");
        sendBlePacket("{\"event\":\"STATUS\",\"state\":\"ESCORTING\"}");
    } else if (cmd.indexOf("RESET") >= 0) {
        stopMotors();
        currentState = STATE_IDLE;
        markersCount = 0;
        activeCardUid = "NONE";
        Serial.println("[CMD] System Reset to IDLE");
        sendBlePacket("{\"event\":\"STATUS\",\"state\":\"IDLE\"}");
    } else if (cmd.indexOf("HELLO") >= 0) {
        sendBlePacket("{\"event\":\"STATUS\",\"state\":\"IDLE\"}");
    } else if (cmd.indexOf("MOVE_FWD") >= 0) {
        int duration = 1500;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 1500;
        executeManualDrive(BASE_DRIVE_SPEED, BASE_DRIVE_SPEED, duration);
        Serial.printf("[CMD] Voice Move Forward (%d ms)\n", duration);
        sendBlePacket("{\"event\":\"MANUAL\",\"action\":\"MOVE_FWD\"}");
    } else if (cmd.indexOf("MOVE_REV") >= 0) {
        int duration = 1500;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 1500;
        executeManualDrive(-BASE_DRIVE_SPEED, -BASE_DRIVE_SPEED, duration);
        Serial.printf("[CMD] Voice Move Backward (%d ms)\n", duration);
        sendBlePacket("{\"event\":\"MANUAL\",\"action\":\"MOVE_REV\"}");
    } else if (cmd.indexOf("TURN_LEFT") >= 0) {
        int duration = 650;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 650;
        executeManualDrive(-TURN_SPEED, TURN_SPEED, duration);
        Serial.printf("[CMD] Voice Turn Left (%d ms)\n", duration);
        sendBlePacket("{\"event\":\"MANUAL\",\"action\":\"TURN_LEFT\"}");
    } else if (cmd.indexOf("TURN_RIGHT") >= 0) {
        int duration = 650;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 650;
        executeManualDrive(TURN_SPEED, -TURN_SPEED, duration);
        Serial.printf("[CMD] Voice Turn Right (%d ms)\n", duration);
        sendBlePacket("{\"event\":\"MANUAL\",\"action\":\"TURN_RIGHT\"}");
    } else if (cmd.indexOf("STOP") >= 0) {
        stopMotors();
        manualDriveActive = false;
        currentState = STATE_IDLE;
        Serial.println("[CMD] Voice Hard Stop");
        sendBlePacket("{\"event\":\"STATUS\",\"state\":\"STOPPED\"}");
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
// 10. ARDUINO SETUP & MAIN LOOP
// ======================================================================================
void setup() {
    Serial.begin(115200);
    Serial.println("\n--- [AURA-EJUST] Starting Minimal Hardware Controller ---");

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

    // Initialize IR Line Sensor Pins
    pinMode(IR_LEFT_PIN, INPUT);
    if (IR_RIGHT_PIN >= 0) pinMode(IR_RIGHT_PIN, INPUT);

    // Initialize Ultrasonic Sensor Pins
    pinMode(TRIG_PIN_1, OUTPUT);
    pinMode(ECHO_PIN_1, INPUT);
    if (TRIG_PIN_2 >= 0) {
        pinMode(TRIG_PIN_2, OUTPUT);
        pinMode(ECHO_PIN_2, INPUT);
    }

    // Initialize BLE Nordic UART Service
    BLEDevice::init("AURA-EJUST-BOT");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new ServerCallbacks());

    BLEService *pService = pServer->createService(SERVICE_UUID);
    pTxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX, BLECharacteristic::PROPERTY_NOTIFY);
    pTxCharacteristic->addDescriptor(new BLE2902());

    pRxCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_RX, BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_WRITE_NR);
    pRxCharacteristic->setCallbacks(new RxCallbacks());

    pService->start();
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->addServiceUUID(SERVICE_UUID);
    pAdvertising->setScanResponse(true);
    pAdvertising->setMinPreferred(0x06);  // Improves discovery on Windows & iOS
    pAdvertising->setMinPreferred(0x12);
    BLEDevice::startAdvertising();

    Serial.println("[BLE] Nordic UART Ready! Device name: AURA-EJUST-BOT");
    Serial.printf("[SYSTEM] %d VIP Cards Registered. Ready for NFC Scan.\n", TOTAL_VIP_CARDS);
}

void loop() {
    // 0. Manual Timed Movement Execution (Voice & BLE Direction Pulses)
    if (manualDriveActive) {
        if (millis() >= manualDriveEndTime) {
            stopMotors();
            manualDriveActive = false;
            curManualLeftSpeed = 0;
            curManualRightSpeed = 0;
            Serial.println("[MANUAL] Timed Drive Complete -> Stopped");
            sendBlePacket("{\"event\":\"MANUAL_DONE\"}");
        } else {
            // Safety brake if obstacle pops up during manual forward drive
            if (curManualLeftSpeed > 0 && curManualRightSpeed > 0) {
                long dist = getMinObstacleDistance();
                if (dist < OBSTACLE_STOP_CM) {
                    stopMotors();
                    manualDriveActive = false;
                    curManualLeftSpeed = 0;
                    curManualRightSpeed = 0;
                    Serial.printf("[OBSTACLE] Manual Drive Halted (%ld cm)\n", dist);
                    sendBlePacket("{\"event\":\"OBSTACLE\",\"dist\":" + String(dist) + "}");
                }
            }
        }
    }

    // BLE Auto-readvertise on disconnect
    if (!deviceConnected && oldDeviceConnected) {
        delay(400);
        pServer->startAdvertising();
        Serial.println("[BLE] Advertising restarted");
        oldDeviceConnected = deviceConnected;
    }
    if (deviceConnected && !oldDeviceConnected) {
        oldDeviceConnected = deviceConnected;
    }

    // Always check for NFC cards when IDLE or ARRIVED
    if (currentState == STATE_IDLE || currentState == STATE_ARRIVED) {
        checkNfcReader();
    }

    // Run Escort Line Following & Obstacle loop
    if (currentState == STATE_ESCORTING) {
        runEscortStep();
    }

    // Periodic 800ms Telemetry to Phone Screen
    unsigned long now = millis();
    if (now - lastTelemetryTime > 800) {
        lastTelemetryTime = now;
        if (deviceConnected) {
            long dist = getMinObstacleDistance();
            int irL = digitalRead(IR_LEFT_PIN);
            int irR = (IR_RIGHT_PIN >= 0) ? digitalRead(IR_RIGHT_PIN) : 0;
            String telem = "{\"event\":\"STATUS\",\"state\":\"" + String(stateStr(currentState)) +
                           "\",\"dist\":" + String(dist) +
                           ",\"ir\":\"" + String(irL) + String(irR) +
                           "\",\"markers\":" + String(markersCount) + "}";
            sendBlePacket(telem);
        }
    }
}
