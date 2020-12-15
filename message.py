class message:
    message_type = 0
    message = None
    NEW_FILE = 1
    NEW_CONNECTION = 2
    BUILD_CONNECTION_SUCCESS = 3
    BUILD_CONNECTION_FAIL = 4

    def __init__(self, message_type, message):
        self.message_type = message_type
        self.message = message

    def __str__(self):
        return str(self.message_type) + str(message)