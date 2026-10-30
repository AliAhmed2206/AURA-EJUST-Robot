/*
 * ======================================================================================
 * AURA-EJUST — AI SCREEN & VOICE CONTROLLED WI-FI FIRMWARE (ESP32)
 * ======================================================================================
 * Integration:
 *   - AI Screen & Voice Brain (AURA Galaxy A24 / WebApp / Gemini 2.5 Flash)
 *   - Autonomous Escort Mission: HQ Door -> Grand Theatre (Line Tracking + Station Markers)
 *   - Voice Driving Navigation: Forward, Reverse, Left, Right, Stop, Wave
 *   - Dual Ultrasonic Active Safety Brakes (Front & Rear Collision Prevention)
 *   - 3-Channel IR Line Tracking (IR_L: 32, IR_C: 23, IR_R: 22)
 *   - High-Speed Non-Blocking Wi-Fi Relay Polling (~120ms latency)
 * ======================================================================================
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ======================================================================================
// 1. WI-FI CREDENTIALS & SECURITY TOKEN CONFIGURATION
// ======================================================================================

// >>> PRE-CONFIGURED WITH YOUR EXACT PHONE HOTSPOT <<<
const char* WIFI_SSID     = "Ali";                 // Hotspot name
const char* WIFI_PASSWORD = "12345679";            // Hotspot password

// Dedicated Security / Auth Token
const char* AURA_AUTH_TOKEN = "AURA-EJUST-VIP-2026-TOKEN";

// Relay Server Address:
// Primary: Local PC Gateway (fastest response on the same Wi-Fi / hotspot)
const char* SERVER_BASE_URL = "http://10.211.82.178:8080";

// Fallback: Public Cloudflare Tunnel (if testing across mobile 4G / separate networks)
const char* CLOUD_TUNNEL_URL = "https://over-tea-cia-remain.trycloudflare.com";

// Active server endpoint
String currentServerUrl = SERVER_BASE_URL;

// ======================================================================================
// 2. HARDWARE PIN DEFINITIONS (Matching Your Exact Robot Wiring)
// ======================================================================================

// ---------- 3-CHANNEL IR LINE SENSORS ----------
#define IR_L 32
#define IR_C 23
#define IR_R 22

// ---------- L293D / L298N MOTOR DRIVER ----------
#define L_IN1 14
#define L_IN2 27
#define L_EN  25

#define R_IN1 26
#define R_IN2 33
#define R_EN  13

// ---------- FRONT ULTRASONIC SENSOR ----------
#define F_TRIG 19
#define F_ECHO 35

// ---------- REAR ULTRASONIC SENSOR ----------
#define B_TRIG 18
#define B_ECHO 34

// ---------- TUNED ROBOT SETTINGS ----------
#define ON_LINE           LOW   // LOW when sensor detects black line
#define SPEED             170   // Normal cruising PWM speed (0-255)
#define TURN_SPEED        200   // Turning adjustment PWM speed
#define OBSTACLE_DISTANCE 15    // Safety stop threshold in cm
#define CMD_POLL_INTERVAL 120   // Non-blocking Wi-Fi command polling interval (ms)
#define TELEMETRY_INTERVAL 1500 // Periodic heartbeat telemetry interval (ms)

// ======================================================================================
// 3. ROBOT STATE MACHINE & MISSIONS
// ======================================================================================
enum RobotState {
    STATE_IDLE,       // Waiting for AI Face instruction or guest greeting
    STATE_ESCORTING,  // Navigating autonomous mission (HQ Door -> Theatre)
    STATE_PAUSED,     // Temporarily halted by obstacle or voice "pause"
    STATE_ARRIVED     // Successfully arrived at destination station (Theatre)
};

RobotState currentState = STATE_IDLE;
String targetDestination = "Theatre"; // Default mission destination
uint8_t targetMarkers = 1;           // 1 cross-line checkpoint from HQ Door to Theatre
uint8_t markersCount = 0;            // Checkpoint markers counter
bool frontObstacleDetected = false;
bool rearObstacleDetected = false;

// Timed Manual Driving State (Directional Voice Commands: "move forward", "turn right", etc.)
bool manualDriveActive = false;
unsigned long manualDriveEndTime = 0;
int curManualLeftSpeed = 0;
int curManualRightSpeed = 0;

// Timing counters
unsigned long lastPollTime = 0;
unsigned long lastTelemetryTime = 0;
unsigned long lastMarkerDebounce = 0;

// ======================================================================================
// 4. MOTOR CONTROL & PWM (Universal ESP32 Core Compatibility)
// ======================================================================================

// Compatible with both ESP32 Arduino Core 2.x and 3.x
#if defined(ESP_ARDUINO_VERSION_MAJOR) && (ESP_ARDUINO_VERSION_MAJOR >= 3)
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

// ======================================================================================
// 5. ULTRASONIC SENSOR READINGS
// ======================================================================================
int distanceCM(int trig, int echo) {
    digitalWrite(trig, LOW);
    delayMicroseconds(2);

    digitalWrite(trig, HIGH);
    delayMicroseconds(10);
    digitalWrite(trig, LOW);

    unsigned long duration = pulseIn(echo, HIGH, 15000); // 15ms timeout ~2.5m range
    if (duration == 0) return 999;
    return duration / 58;
}

// Forward Declarations
void postTelemetry(const String& event, const String& extraJson = "");
void pollRelayCommands();
void handleIncomingCommand(const String& cmd);
void executeManualDrive(int leftSpeed, int rightSpeed, unsigned long durationMs);
const char* stateStr(RobotState s);

// ======================================================================================
// 6. MISSION NAVIGATION: HQ DOOR -> THEATRE (3-IR LINE TRACKING)
// ======================================================================================
void runEscortStep() {
    int frontDist = distanceCM(F_TRIG, F_ECHO);

    // Safety Obstacle Interruption
    if (frontDist < OBSTACLE_DISTANCE) {
        stopRobot();
        if (!frontObstacleDetected) {
            frontObstacleDetected = true;
            Serial.printf("[SAFETY] Obstacle Ahead (%d cm)! Escort Paused\n", frontDist);
            postTelemetry("OBSTACLE", ",\"dist\":" + String(frontDist));
        }
        return;
    } else if (frontObstacleDetected && frontDist >= (OBSTACLE_DISTANCE + 6)) {
        frontObstacleDetected = false;
        Serial.printf("[SAFETY] Path Clear (%d cm)! Resuming Escort\n", frontDist);
        postTelemetry("CLEAR", ",\"dist\":" + String(frontDist));
    }

    // Read 3 IR Sensors
    bool L = (digitalRead(IR_L) == ON_LINE);
    bool C = (digitalRead(IR_C) == ON_LINE);
    bool R = (digitalRead(IR_R) == ON_LINE);

    unsigned long now = millis();

    // CASE 4: Station Marker / T-Junction (All 3 Sensors on Cross-line)
    if (L && C && R) {
        if (now - lastMarkerDebounce > 600) {
            lastMarkerDebounce = now;
            markersCount++;
            Serial.printf("[STATION] Cross-line Marker: %d / %d\n", markersCount, targetMarkers);
            postTelemetry("MARKER", ",\"passed\":" + String(markersCount) + ",\"target\":" + String(targetMarkers));

            if (markersCount >= targetMarkers) {
                stopRobot();
                currentState = STATE_ARRIVED;
                Serial.printf("[DESTINATION] Arrived at %s!\n", targetDestination.c_str());
                postTelemetry("ARRIVED", ",\"dest\":\"" + targetDestination + "\"");
                return;
            }
        }
        // Roll smoothly across the marker line
        moveRobot(SPEED, SPEED);
        return;
    }

    // CASE 1: Line Centered
    if (!L && C && !R) {
        moveRobot(SPEED, SPEED);
    }
    // CASE 2: Drifting Right -> Steer Left
    else if (L && !R) {
        moveRobot(SPEED / 2, TURN_SPEED);
    }
    // CASE 3: Drifting Left -> Steer Right
    else if (R && !L) {
        moveRobot(TURN_SPEED, SPEED / 2);
    }
    // CASE 5: Line Temporarily Lost
    else if (!L && !C && !R) {
        // Check rear ultrasonic before gentle adjustment
        int backDist = distanceCM(B_TRIG, B_ECHO);
        if (backDist > OBSTACLE_DISTANCE) {
            // Gentle reverse nudge to re-acquire the guide line
            moveRobot(-SPEED / 2, -SPEED / 2);
            delay(80);
            stopRobot();
        } else {
            stopRobot();
        }
    }
    // CASE 6: Other sensor patterns (Gentle forward progression)
    else {
        moveRobot(SPEED, SPEED);
    }
}

// ======================================================================================
// 7. WI-FI HTTP RELAY CLIENT (COMMAND POLLING & TELEMETRY)
// ======================================================================================
void postTelemetry(const String& event, const String& extraJson) {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    String url = currentServerUrl + "/api/esp32/telemetry";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(800);

    int frontDist = distanceCM(F_TRIG, F_ECHO);
    int backDist = distanceCM(B_TRIG, B_ECHO);
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
                     ",\"markers\":" + String(markersCount) +
                     extraJson + "}";

    http.POST(payload);
    http.end();
}

int consecutiveFailures = 0;

void pollRelayCommands() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    String url = currentServerUrl + "/api/esp32/command?token=" + String(AURA_AUTH_TOKEN);
    http.begin(url);
    http.setTimeout(650); // 650ms timeout for non-blocking loop

    int httpCode = http.GET();
    if (httpCode == 200) {
        consecutiveFailures = 0;
        String payload = http.getString();
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
    } else {
        consecutiveFailures++;
        if (consecutiveFailures >= 5 && currentServerUrl == SERVER_BASE_URL) {
            Serial.println("[WI-FI] Local LAN response pending. Switching to Cloud Tunnel URL...");
            currentServerUrl = CLOUD_TUNNEL_URL;
            consecutiveFailures = 0;
        } else if (consecutiveFailures >= 10 && currentServerUrl == CLOUD_TUNNEL_URL) {
            currentServerUrl = SERVER_BASE_URL;
            consecutiveFailures = 0;
        }
    }
    http.end();
}

// ======================================================================================
// 8. VOICE & AI SCREEN COMMAND HANDLER
// ======================================================================================
void handleIncomingCommand(const String& cmd) {
    Serial.print("[AI COMMAND RECEIVED] ");
    Serial.println(cmd);

    // 1. Mission: Start Escorting from HQ Door to Theatre
    if (cmd.indexOf("START_ESCORT") >= 0 || cmd.indexOf("ESCORT") >= 0) {
        markersCount = 0;
        targetMarkers = 1; // HQ Door to Grand Theatre = 1 marker station
        targetDestination = "Theatre";
        currentState = STATE_ESCORTING;
        manualDriveActive = false;
        Serial.println("[MISSION] Autonomous Escort to Theatre Started!");
        postTelemetry("MISSION_START", ",\"dest\":\"Theatre\"");
    }
    // 2. Pause / Stop
    else if (cmd.indexOf("PAUSE") >= 0 || cmd.indexOf("STOP") >= 0 || cmd.indexOf("HALT") >= 0) {
        stopRobot();
        manualDriveActive = false;
        currentState = STATE_IDLE;
        Serial.println("[CMD] Robot Stopped");
        postTelemetry("STATUS");
    }
    // 3. Resume Escort
    else if (cmd.indexOf("RESUME") >= 0) {
        currentState = STATE_ESCORTING;
        Serial.println("[CMD] Escort Resumed");
        postTelemetry("STATUS");
    }
    // 4. Directional Voice Driving: Move Forward
    else if (cmd.indexOf("MOVE_FWD") >= 0 || cmd.indexOf("FORWARD") >= 0) {
        int duration = 1500;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 1500;
        executeManualDrive(SPEED, SPEED, duration);
        Serial.printf("[VOICE] Move Forward (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"MOVE_FWD\"");
    }
    // 5. Directional Voice Driving: Move Backward (With Rear Ultrasonic Safety)
    else if (cmd.indexOf("MOVE_REV") >= 0 || cmd.indexOf("BACKWARD") >= 0) {
        int backDist = distanceCM(B_TRIG, B_ECHO);
        if (backDist < OBSTACLE_DISTANCE) {
            stopRobot();
            Serial.printf("[SAFETY] Cannot Reverse! Rear Obstacle at %d cm\n", backDist);
            postTelemetry("OBSTACLE_REAR", ",\"back_dist\":" + String(backDist));
            return;
        }
        int duration = 1500;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 1500;
        executeManualDrive(-SPEED, -SPEED, duration);
        Serial.printf("[VOICE] Move Backward (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"MOVE_REV\"");
    }
    // 6. Directional Voice Driving: Turn Left
    else if (cmd.indexOf("TURN_LEFT") >= 0 || cmd.indexOf("LEFT") >= 0) {
        int duration = 650;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 650;
        executeManualDrive(-TURN_SPEED, TURN_SPEED, duration);
        Serial.printf("[VOICE] Turn Left (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"TURN_LEFT\"");
    }
    // 7. Directional Voice Driving: Turn Right
    else if (cmd.indexOf("TURN_RIGHT") >= 0 || cmd.indexOf("RIGHT") >= 0) {
        int duration = 650;
        int idx = cmd.indexOf("\"ms\":");
        if (idx >= 0) duration = cmd.substring(idx + 5).toInt();
        if (duration <= 0) duration = 650;
        executeManualDrive(TURN_SPEED, -TURN_SPEED, duration);
        Serial.printf("[VOICE] Turn Right (%d ms)\n", duration);
        postTelemetry("MANUAL", ",\"action\":\"TURN_RIGHT\"");
    }
    // 8. Friendly Greeting Wave Gesture
    else if (cmd.indexOf("WAVE") >= 0) {
        Serial.println("[GESTURE] Friendly Waving Motion");
        executeManualDrive(-TURN_SPEED / 2, TURN_SPEED / 2, 220);
        delay(250);
        executeManualDrive(TURN_SPEED / 2, -TURN_SPEED / 2, 220);
        postTelemetry("GESTURE", ",\"action\":\"WAVE\"");
    }
    // 9. Reset System
    else if (cmd.indexOf("RESET") >= 0) {
        stopRobot();
        manualDriveActive = false;
        currentState = STATE_IDLE;
        markersCount = 0;
        Serial.println("[CMD] Reset to IDLE");
        postTelemetry("STATUS");
    }
}

void executeManualDrive(int leftSpeed, int rightSpeed, unsigned long durationMs) {
    // If driving forward, check front ultrasonic
    if (leftSpeed > 0 && rightSpeed > 0) {
        int frontDist = distanceCM(F_TRIG, F_ECHO);
        if (frontDist < OBSTACLE_DISTANCE) {
            stopRobot();
            manualDriveActive = false;
            Serial.printf("[SAFETY] Forward move blocked! Front obstacle at %d cm\n", frontDist);
            postTelemetry("OBSTACLE", ",\"dist\":" + String(frontDist));
            return;
        }
    }
    curManualLeftSpeed = leftSpeed;
    curManualRightSpeed = rightSpeed;
    moveRobot(leftSpeed, rightSpeed);
    manualDriveEndTime = millis() + durationMs;
    manualDriveActive = true;
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
// 9. SETUP
// ======================================================================================
void setup() {
    Serial.begin(115200);
    Serial.println("\n=======================================================");
    Serial.println("  AURA-EJUST — AI SCREEN & VOICE WI-FI CONTROLLER");
    Serial.println("=======================================================");

    // 1. Initialize IR Sensors
    pinMode(IR_L, INPUT);
    pinMode(IR_C, INPUT);
    pinMode(IR_R, INPUT);

    // 2. Initialize Motor Direction & PWM
    pinMode(L_IN1, OUTPUT);
    pinMode(L_IN2, OUTPUT);
    pinMode(R_IN1, OUTPUT);
    pinMode(R_IN2, OUTPUT);
    setupPWM(L_EN, 0);
    setupPWM(R_EN, 1);
    stopRobot();

    // 3. Initialize Dual Ultrasonic Sensors
    pinMode(F_TRIG, OUTPUT);
    pinMode(F_ECHO, INPUT);
    pinMode(B_TRIG, OUTPUT);
    pinMode(B_ECHO, INPUT);

    // 4. Connect to Wi-Fi
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
        Serial.println("\n[WI-FI WARNING] Connection timed out! Will auto-reconnect in loop...");
    }

    Serial.println("=======================================================");
    Serial.println("  SYSTEM READY — WAITING FOR AI VOICE & SCREEN COMMANDS");
    Serial.println("=======================================================\n");
}

// ======================================================================================
// 10. MAIN LOOP
// ======================================================================================
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

    // 2. Poll for AI Voice & Screen Commands (~120ms)
    if (now - lastPollTime >= CMD_POLL_INTERVAL) {
        lastPollTime = now;
        pollRelayCommands();
    }

    // 3. Periodic Heartbeat Telemetry (Every 1500ms)
    if (now - lastTelemetryTime >= TELEMETRY_INTERVAL) {
        lastTelemetryTime = now;
        postTelemetry("HEARTBEAT");
    }

    // 4. Timed Manual Voice Driving ("move forward", "turn left", etc.)
    if (manualDriveActive) {
        if (now >= manualDriveEndTime) {
            stopRobot();
            manualDriveActive = false;
            curManualLeftSpeed = 0;
            curManualRightSpeed = 0;
            Serial.println("[VOICE MOVE] Duration Finished -> Stopped");
        } else if (curManualLeftSpeed > 0 && curManualRightSpeed > 0) {
            // Front safety brake during manual forward movement
            int frontDist = distanceCM(F_TRIG, F_ECHO);
            if (frontDist < OBSTACLE_DISTANCE) {
                stopRobot();
                manualDriveActive = false;
                Serial.printf("[SAFETY] Obstacle during manual forward (%d cm)! Stopped\n", frontDist);
                postTelemetry("OBSTACLE", ",\"dist\":" + String(frontDist));
            }
        }
    }

    // 5. Autonomous Mission Escort (HQ Door -> Theatre)
    if (currentState == STATE_ESCORTING && !manualDriveActive) {
        runEscortStep();
    }

    delay(10); // Smooth RTOS scheduling yield
}
