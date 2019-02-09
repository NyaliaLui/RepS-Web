import hashlib

class FileRenamer:

    def __init__(self, basename='syalper 2cs'):
        self._base = basename
        self._hasher = hashlib.sha224()
        self._hasher.update(self._base)


    def next_available_name(self):
        return self._hasher.hexdigest()