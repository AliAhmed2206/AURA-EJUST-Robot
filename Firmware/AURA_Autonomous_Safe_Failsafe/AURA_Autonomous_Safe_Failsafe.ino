#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>
#include <DabbleESP32.h>

// ======================================================================================
// 1. WIFI & SERVER CONFIGURATION
// ======================================================================================
const char* WIFI_SSID     = "Ali";
const char* WIFI_PASSWORD = "12345679";
const char* TOKEN         = "AURA-EJUST-VIP-2026-TOKEN";
const char* SERVER        = "http://10.103.194.178:8080";

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
// 6. WIFI TELEMETRY (AURA GUEST GREETING)
// ======================================================================================
void postNFC(bool valid, int id, const String& name) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected - telemetry skipped");
        return;
    }

    HTTPClient http;
    http.begin(String(SERVER) + "/api/esp32/telemetry");
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(1500);

    String payload =
        "{\"token\":\"" + String(TOKEN) +
        "\",\"event\":\"NFC_TAP\"" +
        ",\"state\":\"MANUAL\"" +
        ",\"uid\":\"" + activeUID +
        "\",\"guest\":\"" + name +
        "\",\"name\":\"" + name +
        "\",\"valid\":" + String(valid ? "true" : "false") +
        ",\"id\":" + String(id) + "}";

    int responseCode = http.POST(payload);
    Serial.printf("Server response: %d\n", responseCode);
    http.end();
}

// ======================================================================================
// 7. NFC READER
// ======================================================================================
void checkNFC() {
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
// 8. DABBLE GAMEPAD CONTROL (ANALOG JOYSTICK ONLY)
// ======================================================================================
void controlRobot() {
    Dabble.processInput();

    // Read joystick axes (-7 to +7)
    int x = GamePad.getXaxisData();
    int y = GamePad.getYaxisData();

    // Analog joystick control (Deadzone: +-1)
    if (abs(x) > 1 || abs(y) > 1) {
        int left  = constrain(y + x, -7, 7) * 255 / 7;
        int right = constrain(y - x, -7, 7) * 255 / 7;
        motors(left, right);
        return;
    }

    // When joystick is released, stop motors smoothly
    stopMotors();

    /* ----------------------------------------------------------------------------------
     * OPTIONAL DIGITAL D-PAD BUTTON CONTROL (COMMENTED OUT AS REQUESTED)
     * ----------------------------------------------------------------------------------
    if (GamePad.isUpPressed()) {
        motors(180, 180);
    }
    else if (GamePad.isDownPressed()) {
        motors(-180, -180);
    }
    else if (GamePad.isLeftPressed()) {
        motors(-160, 160);
    }
    else if (GamePad.isRightPressed()) {
        motors(160, -160);
    }
    ---------------------------------------------------------------------------------- */
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
    SPI.begin(NFC_SCK, NFC_MISO, NFC_MOSI, NFC_SS);
    rfid.PCD_Init();
    Serial.println("RC522 initialized");

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

    // 3. Lightweight 3-second heartbeat to keep Wi-Fi telemetry active on AURA HUD
    static unsigned long lastHeartbeat = 0;
    if (WiFi.status() == WL_CONNECTED && millis() - lastHeartbeat >= 3000) {
        lastHeartbeat = millis();
        HTTPClient http;
        http.begin(String(SERVER) + "/api/esp32/telemetry");
        http.addHeader("Content-Type", "application/json");
        http.setTimeout(800);
        http.POST("{\"token\":\"" + String(TOKEN) + "\",\"event\":\"HEARTBEAT\",\"state\":\"MANUAL\"}");
        http.end();
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
