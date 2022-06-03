#include "CPP_WebSockets/CPP_WebSockets.hpp"
#include "door/door.hpp"

void actionHandler(String action) {
	if (action == "ACTION_OPEN_DOOR") {
		Serial.println("Opening door...");
		openDoor();
		sendMessage("Opened the door.", "CALLBACK_DOOR_OPENED");
    }
    else if (action == "ACTION_CLOSE_DOOR") {
		Serial.println("Closing door...");
		closeDoor();
		sendMessage("Closed the door.", "CALLBACK_DOOR_CLOSED");
    }
}

void setup() {
	Serial.begin(115200);
	setupWebsocket("CLIENT_ID_ESP_DOOR", actionHandler);
	setupDoor();
}

void loop() {
    websocketLoop(actionHandler);
}