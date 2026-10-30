#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <SPI.h>
#define MFRC522_SPICLOCK 1000000u // 1MHz stable SPI for jumper wires
#include <MFRC522.h>
#define CUSTOM_SETTINGS
#define INCLUDE_GAMEPAD_MODULE
#include <DabbleESP32.h>

// ======================================================================================
// 1. WIFI & SERVER CONFIGURATION
// ======================================================================================
const char* WIFI_SSID     = "Ali";
const char* WIFI_PASSWORD = "12345679";
const char* TOKEN         = "AURA-EJUST-VIP-2026-TOKEN";
const char* SERVER_LAN    = "http://10.103.194.178:8080";
const char* SERVER_TUNNEL = "https://endless-handmade-where-essentially.trycloudflare.com";
bool useTunnel = false;  // Auto-switches to true if LAN fails

// ======================================================================================
// 2. L298N DUAL MOTOR DRIVER PINS
// ======================================================================================
#define L_IN1 14
#define L_IN2 27
#define L_EN  25

#define R_IN1 26
#define R_IN2 33
#define R_EN  13

// ======================================================================================
// 3. RC522 RFID / NFC PINS
// ======================================================================================
#define NFC_SS   5
#define NFC_RST  2
#define NFC_SCK  15
#define NFC_MISO 16
#define NFC_MOSI 17

MFRC522 rfid(NFC_SS, NFC_RST);

// ======================================================================================
// 4. REGISTERED VIP GUEST CARDS TABLE
// ======================================================================================
struct VIPCard {
    const char* uid;
    const char* name;
    int id;
};

const VIPCard cards[] = {
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
    {"53D10572420001", "Marwan Yasser", 14},
    {"53B80572420001", "VIP Guest 14", 14},
    {"53B90572420001", "VIP Guest 15", 15},
    {"53BA0572420001", "VIP Guest 16", 16},
    {"53C00572420001", "VIP Guest 17", 17},
    {"53CB0572420001", "VIP Guest 18", 18},
    {"53D20572420001", "VIP Guest 20", 20},
    {"53E00572420001", "VIP Guest 21", 21}
};

const int CARD_COUNT = sizeof(cards) / sizeof(cards[0]);

unsigned long lastScan = 0;
String activeUID = "NONE";
String activeGuest = "NONE";

// ======================================================================================
// 5. MOTOR CONTROL
// ======================================================================================
void motors(int left, int right) {
    left = constrain(left, -255, 255);
    right = constrain(right, -255, 255);

    // Left motor
    digitalWrite(L_IN1, left > 0);
    digitalWrite(L_IN2, left < 0);
    analogWrite(L_EN, abs(left));

    // Right motor (reversed polarity to drive forward together)
    digitalWrite(R_IN1, right < 0);
    digitalWrite(R_IN2, right > 0);
    analogWrite(R_EN, abs(right));
}

void stopMotors() {
    motors(0, 0);
}

// ======================================================================================
// 6. WIFI TELEMETRY (AURA GUEST GREETING) — Auto LAN→Tunnel failover
// ======================================================================================

// Helper: POST JSON to a URL (HTTP or HTTPS). Returns HTTP status or negative on error.
int postJSON(const String& url, const String& payload) {
    HTTPClient http;
    http.setReuse(false);

    if (url.startsWith("https://")) {
        // HTTPS via Cloudflare tunnel — skip cert verification (trusted tunnel)
        static WiFiClientSecure sslClient;
        sslClient.setInsecure();  // Cloudflare cert — safe for our tunnel
        http.begin(sslClient, url);
    } else {
        http.begin(url);
    }
    http.addHeader("Content-Type", "application/json");
    http.setConnectTimeout(4000);
    http.setTimeout(4000);

    int rc = http.POST(payload);
    http.end();
    return rc;
}

void postNFC(bool valid, int id, const String& name) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected - telemetry skipped");
        return;
    }

    String payload =
        "{\"token\":\"" + String(TOKEN) +
        "\",\"event\":\"NFC_TAP\"" +
        ",\"state\":\"MANUAL\"" +
        ",\"uid\":\"" + activeUID +
        "\",\"guest\":\"" + name +
        "\",\"name\":\"" + name +
        "\",\"valid\":" + String(valid ? "true" : "false") +
        ",\"id\":" + String(id) + "}";

    // Try LAN first (fast), then fall back to Cloudflare tunnel (reliable)
    const char* targets[] = { SERVER_LAN, SERVER_TUNNEL };
    const char* labels[]  = { "LAN", "TUNNEL" };

    for (int t = (useTunnel ? 1 : 0); t < 2; t++) {
        String url = String(targets[t]) + "/api/esp32/telemetry";
        for (int attempt = 1; attempt <= 2; attempt++) {
            int rc = postJSON(url, payload);
            Serial.printf("[NFC POST] %s attempt %d -> %d\n", labels[t], attempt, rc);
            if (rc == 200) {
                Serial.printf("[NFC POST] SUCCESS via %s!\n", labels[t]);
                if (t == 1) useTunnel = true;  // Remember tunnel works
                return;
            }
            delay(250);
        }
    }
    Serial.println("[NFC POST] FAILED via both LAN and TUNNEL");
}

// ======================================================================================
// 7. NFC READER
// ======================================================================================
void checkNFC() {
    static unsigned long lastDebugPrint = 0;
    static bool wasDisconnected = true;
    
    byte ver = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    bool readerOk = (ver != 0x00 && ver != 0xFF);

    if (!readerOk) {
        wasDisconnected = true;
        if (millis() - lastDebugPrint > 2500) {
            lastDebugPrint = millis();
            Serial.printf("[RC522] ?? WIRE LOOSE (0x%02X) - Press/wiggle 3.3V, GND, or MISO (GPIO 16)!\n", ver);
        }
        // Auto-reinitialize as soon as contact is restored
        rfid.PCD_Init();
        return;
    }

    if (wasDisconnected) {
        wasDisconnected = false;
        rfid.PCD_SetAntennaGain(MFRC522::RxGain_max);
        Serial.printf("[RC522] ? CONTACT RESTORED (Firmware: 0x%02X) - READY TO SCAN!\n", ver);
    }

    if (millis() - lastDebugPrint > 5000) {
        lastDebugPrint = millis();
        Serial.printf("[RC522] Active & Scanning OK (0x%02X) - Hold card against reader...\n", ver);
    }

    if (!rfid.PICC_IsNewCardPresent()) return;
    if (!rfid.PICC_ReadCardSerial()) return;

    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        if (rfid.uid.uidByte[i] < 0x10) uid += "0";
        uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();

    // 3.5s cooldown to prevent accidental repeated scans of the same card
    if (uid == activeUID && millis() - lastScan < 3500) {
        return;
    }

    lastScan = millis();
    activeUID = uid;

    bool valid = false;
    int id = 0;
    String name = "UNKNOWN";

    // Search registered VIP cards
    for (int i = 0; i < CARD_COUNT; i++) {
        if (uid == cards[i].uid) {
            valid = true;
            id = cards[i].id;
            name = cards[i].name;
            break;
        }
    }

    activeGuest = name;

    Serial.println("-------------------------");
    Serial.print("NFC UID: ");
    Serial.println(uid);
    Serial.print("Guest: ");
    Serial.println(name);
    Serial.print("Valid: ");
    Serial.println(valid ? "YES" : "NO");
    Serial.println("-------------------------");

    postNFC(valid, id, name);
}

// ======================================================================================
// 8. DABBLE GAMEPAD CONTROL (ANALOG JOYSTICK & DIGITAL D-PAD)
// ======================================================================================
void controlRobot() {
    Dabble.processInput();

    // 1. Analog joystick mode (-7 to +7)
    int x = GamePad.getXaxisData();
    int y = GamePad.getYaxisData();

    if (abs(x) > 1 || abs(y) > 1) {
        int left  = constrain(y + x, -7, 7) * 255 / 7;
        int right = constrain(y - x, -7, 7) * 255 / 7;
        motors(left, right);
        return;
    }

    // 2. Digital D-Pad button mode (Up, Down, Left, Right arrows)
    if (GamePad.isUpPressed()) {
        motors(200, 200);   // Forward
        return;
    } else if (GamePad.isDownPressed()) {
        motors(-200, -200); // Backward
        return;
    } else if (GamePad.isLeftPressed()) {
        motors(-180, 180);  // Spin Left
        return;
    } else if (GamePad.isRightPressed()) {
        motors(180, -180);  // Spin Right
        return;
    }

    // 3. When neither joystick nor buttons are pressed, stop motors smoothly
    stopMotors();
}

// ======================================================================================
// 9. SETUP
// ======================================================================================
void setup() {
    Serial.begin(115200);

    // Motor pins initialization
    pinMode(L_IN1, OUTPUT);
    pinMode(L_IN2, OUTPUT);
    pinMode(L_EN, OUTPUT);

    pinMode(R_IN1, OUTPUT);
    pinMode(R_IN2, OUTPUT);
    pinMode(R_EN, OUTPUT);

    stopMotors();

    // NFC RC522 initialization
        pinMode(NFC_MISO, INPUT_PULLUP); // Prevent floating MISO line
    SPI.begin(NFC_SCK, NFC_MISO, NFC_MOSI, NFC_SS);
    rfid.PCD_Init();
    delay(50);
    rfid.PCD_SetAntennaGain(MFRC522::RxGain_max); // Set antenna sensitivity to MAX 48dB
    rfid.PCD_DumpVersionToSerial();               // Official diagnostic dump
    byte ver = rfid.PCD_ReadRegister(MFRC522::VersionReg);
    Serial.printf("RC522 firmware version: 0x%02X\n", ver);
    if (ver == 0x00 || ver == 0xFF) {
        Serial.println("=================================================");
        Serial.println("!! ERROR: RC522 HARDWARE NOT DETECTED !!");
        Serial.println("Please check physical wiring:");
        Serial.println("  RC522 3.3V  -> ESP32 3V3 (NOT 5V!)");
        Serial.println("  RC522 GND   -> ESP32 GND");
        Serial.println("  RC522 SDA/SS-> ESP32 GPIO 5");
        Serial.println("  RC522 SCK   -> ESP32 GPIO 15");
        Serial.println("  RC522 MOSI  -> ESP32 GPIO 17");
        Serial.println("  RC522 MISO  -> ESP32 GPIO 16");
        Serial.println("  RC522 RST   -> ESP32 GPIO 2");
        Serial.println("=================================================");
    } else {
        Serial.println("[OK] RC522 hardware initialized with MAX 48dB sensitivity!");
    }

    // WiFi initialization
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting to WiFi");
    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
        delay(250);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected");
        Serial.print("ESP32 IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("\nWiFi unavailable - NFC & Dabble remain active");
    }

    // Dabble Bluetooth initialization
    Dabble.begin("AURA-ESP32");

    Serial.println("-------------------------");
    Serial.println("AURA ESP32 READY");
    Serial.println("NFC System: READY");
    Serial.println("Dabble Bluetooth: READY");
    Serial.println("Motor Driver: READY");
    Serial.println("-------------------------");
}

// ======================================================================================
// 10. MAIN LOOP
// ======================================================================================
void loop() {
    // 1. Read NFC cards & post telemetry to AURA
    checkNFC();

    // 2. Control robot via Dabble analog joystick
    controlRobot();

    // 3. Lightweight heartbeat to keep Wi-Fi telemetry active on AURA HUD
    static unsigned long lastHeartbeat = 0;
    if (WiFi.status() == WL_CONNECTED && millis() - lastHeartbeat >= 5000) {
        lastHeartbeat = millis();
        String hbPayload = "{\"token\":\"" + String(TOKEN) + "\",\"event\":\"HEARTBEAT\",\"state\":\"MANUAL\"}";
        String url = String(useTunnel ? SERVER_TUNNEL : SERVER_LAN) + "/api/esp32/telemetry";
        int hb = postJSON(url, hbPayload);
        static bool lastOk = true;
        bool ok = (hb == 200);
        if (!ok && !useTunnel) {
            // LAN failed — try tunnel for heartbeat too
            url = String(SERVER_TUNNEL) + "/api/esp32/telemetry";
            hb = postJSON(url, hbPayload);
            ok = (hb == 200);
            if (ok) { useTunnel = true; Serial.println("[HB] Switched to TUNNEL mode"); }
        }
        if (ok != lastOk) {
            Serial.println(ok ? "[HB] Bridge reachable" : "[HB] Bridge UNREACHABLE - check laptop");
            lastOk = ok;
        }
    }

    // 4. Reconnect WiFi if disconnected
    if (WiFi.status() != WL_CONNECTED) {
        static unsigned long lastReconnect = 0;
        if (millis() - lastReconnect >= 5000) {
            lastReconnect = millis();
            WiFi.reconnect();
        }
    }
}
