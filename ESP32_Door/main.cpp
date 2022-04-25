/*
	Minimal Esp32 Websockets Client

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

const char* ssid = "SSID"; //Enter SSID
const char* password = "PASSWORD"; //Enter Password
const char* websockets_server_host = "192.168.1.158"; //Enter server adress
const uint16_t websockets_server_port = 8888; // Enter server port

using namespace websockets;

WebsocketsClient client;
String client_id = "CLIENT_ID_ESP_DOOR";

void sendChat(String message, String user = "Door/Fan") {
    client.send("{\"client_id\": \"" + client_id + "\", \"action\": \"ACTION_CHAT\", \"data\": {\"user\": \"" + user + "\", \"message\": \"" + message + "\"}}");
}

void onMessageCallback(WebsocketsMessage message) {

    // Allocate the JSON document
    //
    // Inside the brackets, 200 is the capacity of the memory pool in bytes.
    // Don't forget to change this value to match your JSON document.
    // Use https://arduinojson.org/v6/assistant to compute the capacity.
    StaticJsonDocument<200> doc;

    // StaticJsonDocument<N> allocates memory on the stack, it can be
    // replaced by DynamicJsonDocument which allocates in the heap.
    //
    // DynamicJsonDocument doc(200);

    // JSON input string.
    //
    // Using a char[], as shown here, enables the "zero-copy" mode. This mode uses
    // the minimal amount of memory because the JsonDocument stores pointers to
    // the input buffer.
    // If you use another type of input, ArduinoJson must copy the strings from
    // the input to the JsonDocument, so you need to increase the capacity of the
    // JsonDocument.
    // Serial.println(message.data());

    // Deserialize the JSON document
    DeserializationError error = deserializeJson(doc, message.data());

    // Test if parsing succeeds.
    if (error) {
      Serial.print(F("deserializeJson() failed: "));
      Serial.println(error.f_str());
      return;
    }

    String action = doc["action"].as<String>();
    if(action == "ACTION_CHAT") {
      // std::string a = (std::string)doc["action"].as<char*>();
      Serial.println(action + " | " + doc["data"]["user"].as<String>() + ": " + doc["data"]["message"].as<String>());
      if(doc["client_id"].as<String>() != client_id) {
          sendChat("I received something! Pong!");
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
    // Serial.println(data);
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

    sendChat("Hey y'all, I've joined the system. It's my task to open/close the door and to turn the fan on/off.");

    // Send a ping
    // client.ping();
}

void setup() {
    Serial.begin(115200);

    connectWiFi();

    connectSocket();
}

void loop() {
    client.poll();
    if(not client.available()) {
        Serial.println("WebSocket server is unavailable. Connecting...");
        connectSocket();
        delay(5000);
    }
}