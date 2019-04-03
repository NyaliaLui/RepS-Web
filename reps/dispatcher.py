from multiprocessing import Queue
from folder_processor import FolderProcessor
from reps.archiver import ZipArchiver, RARArchiver
from renamer import FileRenamer
import os
from shutil import move

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
        self._archiver = None

    #extract_replays
    # @params - the source folder where zip archive is and destination folder to extract replays to
    # @return - no return
    # @purpose - to extract the sc2 replays from a zip archive
    def __extract_replays(self, src, dest):
        file_path = os.path.join(self._upload_folder, src)
        target_path = os.path.join(self._replay_folder, dest)

        if self._archiver is None:
            raise Exception('archiver was not defined')
        else:
            self._archiver.extract(file_path, target_path)

    #archive_replays
    # @params - the directory where archiving should start
    # @return - no return value
    # @purpose - form an archive of SC2 replays
    def __archive_replays(self, dirname):
        dir_path = os.path.join(self._replay_folder, dirname)
        file_name = 'Replays' + self._archiver.extension

        os.chdir(dir_path)

        self._archiver.create(file_name, 'Replays')

        os.chdir(self._root)

    #dispatch
    # @params - name of the archive and sort option with repay renaming set to false by default
    # @return - the directory which holds the sorted archive
    # @purpose - extract, sort, and re-zip the archive
    def dispatch(self, archive_name, sortop, enable_rename=False):

        directory = archive_name[:-4]
        extension = archive_name[-4:]

        if extension == '.zip':
            self._archiver = ZipArchiver()
            print("zip found")
        elif extension == '.rar':
            self._archiver = RARArchiver()
            print("rar found")

        #unzip file to /replays/<archive_name w/o extension>
        self.__extract_replays(src=archive_name, dest=directory)

        #run RepS
        target = os.path.join(self._replay_folder, directory)
        fp = FolderProcessor(target)
        fp.organize_replays(target, sortop, enable_rename)

        #zip /Replays
        self.__archive_replays(directory)

        #rename files for archival purposes
        name = self._renamer.next_available_name()
        olddir = target
        newdir = os.path.join(self._replay_folder, name)
        move(olddir, newdir)

        old_archive = os.path.join(self._upload_folder, archive_name)
        new_archive = os.path.join(self._upload_folder, name+extension)
        move(old_archive, new_archive)

        #return the directory where sorted replays were uploaded
        return name