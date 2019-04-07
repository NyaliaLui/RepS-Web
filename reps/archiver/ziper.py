from zipfile import ZipFile
import os

#ZipArchiver
# @purpose - the archiver which can extract and create zip archives
class ZipArchiver:

    def __init__(self):
        self.extension = '.zip'

    #get_all_file_paths
    # @params - the directory to walk through
    # @return - list of file paths
    # @purpose - to determine the paths to all files in a directory
    def __get_all_file_paths(self, directory):
    
        file_paths = [] 
    
        for root, directories, files in os.walk(directory): 
            for filename in files: 
                filepath = os.path.join(root, filename) 
                file_paths.append(filepath) 
    
        return file_paths 

    #extract
    # @params - the path to source zip file and path to destination
    #   where the contents will be written
    # @return - no return values
    # @purpose - extract the contents of a zip archive
    def extract(self, src, dest):
        with ZipFile(src, 'r') as zip:
            zip.extractall(path=dest)
    

    #create
    # @params - the name to give the archive and the directory to start compression
    # @return - no return values
    # @purpose - create a zip archive with the given name.
    def create(self, archive_name, archive_root):

        file_paths = self.__get_all_file_paths(archive_root)

        with ZipFile(archive_name, 'w') as zip: 
            # writing each file one by one 
            for file in file_paths:
                zip.write(file)
