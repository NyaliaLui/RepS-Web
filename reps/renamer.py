#FileRenamer
# @purpose - an object used to get the next available names using the RepS naming scheme
class FileRenamer:

    def __init__(self, basename='syalper-'):
        self._base = basename
        self._count = 0

    #next_available_name
    # @params - no params
    # @return - the next available file name
    # @purpose - return the next available file name following the RepS naming scheme
    def next_available_name(self):
        name = self._base + str(self._count)
        self._count = self._count + 1
        return name