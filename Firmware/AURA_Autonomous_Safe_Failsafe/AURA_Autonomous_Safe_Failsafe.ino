#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <MFRC522.h>

// ---------- WIFI / SERVER ----------
const char* WIFI_SSID = "Ali";
const char* WIFI_PASSWORD = "12345679";
const char* TOKEN = "AURA-EJUST-VIP-2026-TOKEN";
const char* SERVER = "http://10.103.194.178:8080";

// ---------- RC522 PINS ----------
#define NFC_SS   5
#define NFC_RST  2
#define NFC_SCK  15
#define NFC_MISO 16
#define NFC_MOSI 17

MFRC522 rfid(NFC_SS, NFC_RST);

// ---------- VIP CARDS ----------
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
String activeUID = "";

// ---------- SEND TO SERVER ----------
void postNFC(bool valid, int id, const String& name) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi disconnected. Event not sent.");
    return;
  }

  HTTPClient http;
  http.begin(String(SERVER) + "/api/esp32/telemetry");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(2000);

  String payload =
    "{\"token\":\"" + String(TOKEN) +
    "\",\"event\":\"NFC_TAP\"" +
    ",\"state\":\"STANDBY\"" +
    ",\"uid\":\"" + activeUID +
    "\",\"guest\":\"" + name +
    "\",\"name\":\"" + name +
    "\",\"valid\":" + String(valid ? "true" : "false") +
    ",\"id\":" + String(id) + "}";

  int response = http.POST(payload);

  Serial.printf("Server response: %d\n", response);

  http.end();
}

// ---------- NFC READER ----------
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

  if (uid == activeUID && millis() - lastScan < 3500) return;

  activeUID = uid;
  lastScan = millis();

  bool valid = false;
  int id = 0;
  String name = "UNKNOWN";

  for (int i = 0; i < CARD_COUNT; i++) {
    if (uid == cards[i].uid) {
      valid = true;
      id = cards[i].id;
      name = cards[i].name;
      break;
    }
  }

  Serial.println("------------------------");
  Serial.println("NFC SCANNED");
  Serial.println("UID: " + uid);
  Serial.println("Guest: " + name);
  Serial.println("Status: " + String(valid ? "VALID" : "UNKNOWN"));

  postNFC(valid, id, name);
}

// ---------- SETUP ----------
void setup() {
  Serial.begin(115200);

  SPI.begin(NFC_SCK, NFC_MISO, NFC_MOSI, NFC_SS);
  rfid.PCD_Init();

  Serial.println("Connecting to WiFi...");

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED &&
         millis() - start < 10000) {
    delay(250);
    Serial.print(".");
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWiFi connected!");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nWiFi unavailable. NFC remains active.");
  }

  Serial.println("NFC READY - Scan a VIP card");
}

// ---------- LOOP ----------
void loop() {
  checkNFC();

  // Send lightweight 3-second heartbeat to keep Wi-Fi telemetry active on AURA HUD
  static unsigned long lastHeartbeat = 0;
  if (WiFi.status() == WL_CONNECTED && millis() - lastHeartbeat >= 3000) {
    lastHeartbeat = millis();
    HTTPClient http;
    http.begin(String(SERVER) + "/api/esp32/telemetry");
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(800);
    http.POST("{\"token\":\"" + String(TOKEN) + "\",\"event\":\"HEARTBEAT\",\"state\":\"STANDBY\"}");
    http.end();
  }

  static unsigned long lastReconnect = 0;

  if (WiFi.status() != WL_CONNECTED &&
      millis() - lastReconnect >= 5000) {
    lastReconnect = millis();
    WiFi.reconnect();
  }
}