/*
	This sketch:
        1. Connects to a WiFi network
        2. Connects to a Websockets server
        3. Sends the websockets server a message ("Hello Server")
        4. Sends the websocket server a "ping"
        5. Prints all incoming messages while the connection is open

    NOTE:
    The sketch dosen't check or indicate about errors while connecting to 
    WiFi or to the websockets server. For full example you might want 
    to try the example named "Esp32-Client".

	Hardware:
        For this sketch you only need an ESP8266 board.

	Created 15/02/2019
	By Gil Maimon
	https://github.com/gilmaimon/ArduinoWebsockets
*/
#include <ArduinoWebsockets.h>
#include <WiFi.h>
#include <ArduinoJson.h>
using namespace websockets;

const char* ssid = "LAPTOP-JESSE"; //Enter SSID
const char* password = "D1SL4PT0P"; //Enter Password
const char* websockets_server_host = "192.168.137.134"; //Enter server adress
const uint16_t websockets_server_port = 8888; // Enter server port

unsigned long keepAlivePrevMillis = 0;
const unsigned long keepAliveIntervalMs = 10000;

WebsocketsClient client;
String client_id = "CLIENT_ID_UNKNOWN_ESP";

void sendData(String action = "ACTION_CHAT", String json_data_string = "\"{\"user\": \"Door/Fan\", \"message\": \"None\"}\"") {
    client.send("{\"client_id\": \"" + client_id + "\", \"action\": \"" + action + "\", \"data\": " + json_data_string + "}");
}

void sendMessage(String message, String action = "ACTION_CHAT", String user = "Door/Fan") {
    sendData(action, "{\"user\": \"" + user + "\", \"message\": \"" + message + "\"}");
}

void onMessageCallback(WebsocketsMessage message) {

    // Allocate the JSON document
    StaticJsonDocument<600> doc;

    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, message.data());

    // Test if parsing succeeds.
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }

    String action = doc["action"].as<String>();

    // if message received is a chat message:
    if(action == "ACTION_CHAT") {
      Serial.println(action + " | " + doc["data"]["user"].as<String>() + ": " + doc["data"]["message"].as<String>());
      if(doc["client_id"].as<String>() != client_id) {
        //   sendMessage("I received something! Pong!");
      }
    }
}

void onEventsCallback(WebsocketsEvent event, String data) {
    if(event == WebsocketsEvent::ConnectionOpened) {
        Serial.println("Connnection opened.");
    } else if(event == WebsocketsEvent::ConnectionClosed) {
      Serial.println("Lost connection.");
    } else if(event == WebsocketsEvent::GotPing) {
        Serial.println("Got a Ping!");
    } else if(event == WebsocketsEvent::GotPong) {
        Serial.println("Got a Pong!");
    }
}

void connectWiFi() {
    // Connect to wifi
    WiFi.begin(ssid, password);

    // Wait some time to connect to wifi
    Serial.print("Connecting to WiFi");
    for(int i = 0; i < 10 && WiFi.status() != WL_CONNECTED; i++) {
        Serial.print(".");
        delay(1000);
    }
    Serial.println();
}

void connectSocket() {
    // run callback when messages are received
    client.onMessage(onMessageCallback);
    
    // run callback when events are occuring
    client.onEvent(onEventsCallback);

    // Connect to server
    client.connect(websockets_server_host, websockets_server_port, "/websocket");

    // Send a message
    sendMessage("Hey y'all, I've joined the system. It's my task to open/close the door and to turn the fan on/off.");
}

void setupWebsocket(String _client_id) {
    client_id = _client_id;
    connectWiFi();
    connectSocket();
}

void websocketLoop() {
    client.poll();

    if (millis() - keepAlivePrevMillis >= keepAliveIntervalMs) {
        keepAlivePrevMillis = millis();
        sendMessage("Keeping connection alive.", "ACTION_ALIVE");
    }

    if(not client.available()) {
        Serial.println("WebSocket server is unavailable. Connecting...");
        connectSocket();
        delay(5000);
    }
}