#include <ArduinoWebsockets.h>
#include <WiFi.h>
#include <ArduinoJson.h>

void sendMessage(String message, String action = "ACTION_CHAT", String user = "Door/Fan/Temperature/Humidity");
void setupWebsocket(String _client_id);
void websocketLoop();
void sendData(String action = "ACTION_CHAT", String json_data_string = "\"{\"user\": \"Door/Fan\", \"message\": \"None\"}\"");
void sendMessage();