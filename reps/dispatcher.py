from multiprocessing import Queue
from folder_processor import FolderProcessor
from renamer import FileRenamer
import os
from shutil import move
from zipfile import ZipFile

#Dispatcher
# @purpose - an object manager that maintains a record of serveral Sorters. Using the dispatch() method
#  a zip archive will be sent to a Sorter for extraction, sorting, and re-zipping.
class Dispatcher:

    #max_sorters - maximum number of sorters allowed at a time
    #running_sorters - current number of running sorters
    #sorters - the list of sorters
    #result_queue - queue for the resulting zip archives which sorters creates
    #waiting_queue - queue for zip archives that are currently waiting to be sorted

    def __init__(self, root):
        self._root = root
        self._upload_folder = os.path.join(root, 'uploads')
        self._replay_folder = os.path.join(root, 'replays')
        self._replays_zip = 'Replays.zip'
        self._renamer = FileRenamer()

    #extract_replays
    # @params - the source folder where zip archive is and destination folder to extract replays to
    # @return - no return
    # @purpose - to extract the sc2 replays from a zip archive
    def __extract_replays(self, src, dest):
        file_path = os.path.join(self._upload_folder, src)
        target_path = os.path.join(self._replay_folder, dest)

        with ZipFile(file_path, 'r') as zip:
            zip.extractall(path=target_path)

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

    #zip_replays
    # @params - the directory where zipping should start
    # @return - no return value
    # @purpose - zip a directory into a .zip file
    def __zip_replays(self, dirname):
        dir_path = os.path.join(self._replay_folder, dirname)
        os.chdir(dir_path)

        file_paths = self.__get_all_file_paths('Replays')

        with ZipFile(self._replays_zip, 'w') as zip: 
            # writing each file one by one 
            for file in file_paths:
                zip.write(file)

        os.chdir(self._root)

    #dispatch
    # @params - name of the archive and sort option
    # @return - the directory which holds the sorted archive
    # @purpose - extract, sort, and re-zip the archive
    def dispatch(self, archive_name, sortop):

        directory = archive_name[:-4]

        #unzip file to /replays/<archive_name w/o extension>
        self.__extract_replays(src=archive_name, dest=directory)

        #run RepS
        target = os.path.join(self._replay_folder, directory)
        fp = FolderProcessor(target)
        fp.organize_replays(target, sortop)

        #zip /Replays
        self.__zip_replays(directory)

        #rename files for archival purposes
        name = self._renamer.next_available_name()
        olddir = target
        newdir = os.path.join(self._replay_folder, name)
        move(olddir, newdir)

        oldzip = os.path.join(self._upload_folder, archive_name)
        newzip = os.path.join(self._upload_folder, name+'.zip')
        move(oldzip, newzip)

        #return the directory where sorted replays were uploaded
        return name