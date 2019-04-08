#RepsError
# @purpose - serve as the Exception when erros occur in RepS.
#           Will use names list to store the file names and state of system
#           when exceptino occured.
class RepsError(Exception):

    #names - list of file names. the system state is based on file names
    def __init__(self, names):
        self.names = names
    
    def __str__(self):
        return repr(self.names)