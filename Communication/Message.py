import json
from types import SimpleNamespace

CLIENT_ID_LOGIC = "CLIENT_ID_LOGIC"
CLIENT_ID_SERVER = "CLIENT_ID_SERVER"
CLIENT_ID_DASHBOARD = "CLIENT_ID_DASHBOARD"
CLIENT_ID_ESP_TEMPERATURE_HUMIDITY = "CLIENT_ID_ESP_TEMPERATURE_HUMIDITY"
CLIENT_ID_ESP_DOOR = "CLIENT_ID_ESP_DOOR"

ACTION_ALIVE = "ACTION_ALIVE"
ACTION_CHAT = "ACTION_CHAT"
ACTION_RICKROLL = "ACTION_RICKROLL"
ACTION_OPEN_DOOR = "ACTION_OPEN_DOOR"
ACTION_CLOSE_DOOR = "ACTION_CLOSE_DOOR"
ACTION_STATUS_UPDATE = "ACTION_STATUS_UPDATE"
ACTION_STATUS_HISTORY = "ACTION_STATUS_HISTORY"
ACTION_MEASURED_TEMPERATURE_AND_HUMIDITY_OUTSIDE = "ACTION_MEASURED_TEMPERATURE_AND_HUMIDITY_OUTSIDE"
ACTION_ACTIVATE_DO_NOT_DISTURB = "ACTION_ACTIVATE_DO_NOT_DISTURB"
ACTION_DEACTIVATE_DO_NOT_DISTURB = "ACTION_DEACTIVATE_DO_NOT_DISTURB"

ACTION_SET_BUSY_IN_15_MINUTES = "ACTION_SET_BUSY_IN_15_MINUTES"
ACTION_SET_NOT_BUSY_IN_15_MINUTES = "ACTION_SET_NOT_BUSY_IN_15_MINUTES"

CALLBACK_DOOR_OPENED = "CALLBACK_DOOR_OPENED"
CALLBACK_DOOR_CLOSED = "CALLBACK_DOOR_CLOSED"
# ACTION_SPEAKER = "ACTION_SPEAKER"

class Message(object):
    def __init__(self, client_id, action, data):
        self.client_id = client_id
        self.action = action
        self.data = data
        
    def fromJSON(self, jsonString):
        # print(jsonString,"\n")
        dictionary = json.loads(jsonString)
        return self.fromDictionary(dictionary)
    
    def fromDictionary(self, dictionary):
        self.client_id = dictionary["client_id"]
        self.action = dictionary["action"]
        self.data = dictionary["data"]
        return self
        
    def toJSON(self):
        return json.dumps({"client_id": self.client_id, "action": self.action, "data": self.data})