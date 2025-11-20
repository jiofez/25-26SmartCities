interface de premiere utilisation idée
➡️ Le Raspberry crée un WiFi temporaire de configuration (ex : Nichoir-Setup)
➡️ L’utilisateur s’y connecte
➡️ Il accède à une interface web sur le serveur
➡️ Le serveur récupère SSID + mot de passe
➡️ Le serveur configure l’ESP32 via :

MQTT

HTTP REST

Bluetooth BLE
➡️ L’ESP32 reçoit les paramètres → se connecte au vrai WiFi
