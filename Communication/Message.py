import json
from types import SimpleNamespace

CLIENT_ID_LOGIC = "CLIENT_ID_LOGIC"
CLIENT_ID_SERVER = "CLIENT_ID_SERVER"
CLIENT_ID_DASHBOARD = "CLIENT_ID_DASHBOARD"
CLIENT_ID_ESP_DOOR = "CLIENT_ID_ESP_DOOR"
ACTION_CHAT = "ACTION_CHAT"
ACTION_ALIVE = "ACTION_ALIVE"
# ACTION_SPEAKER = "ACTION_SPEAKER"

class Message(object):
    def __init__(self, client_id, action, data):
        self.client_id = client_id
        self.action = action
        self.data = data
        
    def fromJSON(self, jsonString):
        # print(jsonString,"\n")
        j = json.loads(jsonString)
        self.client_id = j["client_id"]
        self.action = j["action"]
        self.data = j["data"]
        return self
        
    def toJSON(self):
        return json.dumps({"client_id": self.client_id, "action": self.action, "data": self.data})