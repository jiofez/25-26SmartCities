#include "M5TimerCAM.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include "base64.h"

// ---------------- WiFi ----------------
const char* ssid = "electroProjectWifi";
const char* password = "B1MesureEnv";

// ---------------- MQTT ----------------
const char* mqtt_server = "192.168.2.11";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

// Taille du chunk (800 chars = OK) — doit être multiple de 4
const size_t CHUNK_SIZE = 800;

void setup_wifi() {
    Serial.print("📡 Connexion WiFi...");
    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✅ WiFi connecté !");
}

void reconnect() {
    while (!client.connected()) {
        Serial.print("🔄 Connexion MQTT...");
        String clientId = "TimerCAM-" + String(WiFi.macAddress());
        if (client.connect(clientId.c_str())) {
            Serial.println("✅ MQTT connecté !");
        } else {
            Serial.print("❌ MQTT rc=");
            Serial.println(client.state());
            delay(3000);
        }
    }
}

void sendImageMQTT() {

    if (!TimerCAM.Camera.get()) {
        Serial.println("❌ Erreur capture image");
        return;
    }

    uint8_t* buf = TimerCAM.Camera.fb->buf;
    size_t length = TimerCAM.Camera.fb->len;

    Serial.printf("📷 Image capturée : %d bytes\n", length);

    // 1️⃣ Encodage Base64 complet
    String imgB64 = base64::encode(buf, length);

    TimerCAM.Camera.free();

    Serial.printf("📦 Taille Base64 : %d chars\n", imgB64.length());

    // 2️⃣ Envoyer signal de début
    client.publish("nichoir/image/start", "1");

    // 3️⃣ Découpage à la bonne taille (multiple de 4)
    for (size_t i = 0; i < imgB64.length(); i += CHUNK_SIZE) {
        size_t end = (i + CHUNK_SIZE > imgB64.length()) ? imgB64.length() : i + CHUNK_SIZE;

        String chunk = imgB64.substring(i, end);

        // Sécurité : forcer multiple de 4
        int remainder = chunk.length() % 4;
        if (remainder != 0) {
            chunk = chunk.substring(0, chunk.length() - remainder);
        }

        if (!client.publish("nichoir/image/chunk", chunk.c_str())) {
            Serial.println("❌ Échec envoi chunk MQTT");
        }

        delay(10);
    }

    // 4️⃣ Envoyer fin
    client.publish("nichoir/image/end", "1");

    Serial.println("✅ Image envoyée en chunks Base64 !");
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n🚀 TimerCAM MQTT Sender");

    // Init caméra
    TimerCAM.begin();
    if (!TimerCAM.Camera.begin()) {
        Serial.println("❌ Camera Init Fail");
        while (1);
    }
    Serial.println("✅ Camera Init Success");

    // Init réseau
    setup_wifi();
    client.setServer(mqtt_server, mqtt_port);
    client.setBufferSize(4096);
}

void loop() {
    if (!client.connected()) reconnect();
    client.loop();

    sendImageMQTT();
    delay(8000);
}
