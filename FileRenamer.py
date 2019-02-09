class FileRenamer:

    def __init__(self, basename='syalper-'):
        self._base = basename
        self._count = 0

    def next_available_name(self):
        name = self._base + str(self._count)
        self._count = self._count + 1
        return name