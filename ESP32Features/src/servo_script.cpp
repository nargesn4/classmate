#include "CPP_WebSockets/CPP_WebSockets.hpp"
#include "door/door.hpp"

void actionHandler(String action) {
	if (action == "ACTION_OPEN_DOOR") {
		Serial.println("Opening door...");
		// if (!doorOpen) {
			openDoor();
			// doorOpen = true;
		// }
		sendMessage("Opened the door.", "CALLBACK_DOOR_OPENED");
    }
    else if (action == "ACTION_CLOSE_DOOR") {
		Serial.println("Closing door...");
		// if (doorOpen) {
			closeDoor();
			// doorOpen = false;
		// }
		sendMessage("Closed the door.", "CALLBACK_DOOR_CLOSED");
    }
}

void setup() {
	Serial.begin(115200);
	setupWebsocket("CLIENT_ID_ESP_DOOR", actionHandler);
	setupDoor();

	// closeDoor();
	// doorOpen = false;
}

void loop() {
    websocketLoop(actionHandler);
}