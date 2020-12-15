class SharedFile(object):
    mtime = ""
    size = ""
    filename = ""
    def __init__(self, filename, mtime, size):
        self.filename = filename
        self.mtime = mtime
        self.size = size

    def __eq__(self, other):
        return self.filename == other.filename

    def __hash__(self):
        return hash(self.filename)