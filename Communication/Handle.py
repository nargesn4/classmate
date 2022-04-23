import Communication

class Handle(Communication.Message):
    def __init__(self, message):
        self.message = message