class message:
    message_type = 0
    message = None
    NEW_FILE = 1
    NEW_TICKET = 2
    FILE_BLOCK = 3

    def __init__(self, message_type, message):
        """
        message:
            type           message
            NEW_FILE       new_file_list {filename: sharedFile}
            NEW_TICKET     TICKET
            FILE_BLOCK     (Block, index)
        :rtype: object
        """
        self.message_type = message_type
        self.message = message

