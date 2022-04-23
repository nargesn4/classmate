
class Message(object):
    def __init__(self, client_id, action, data):
        self.client_id = client_id
        self.action = action
        self.data = data