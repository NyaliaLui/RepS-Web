from os import listdir, chdir, mkdir, rename
from os.path import isdir, join
from shutil import copy as cp
from reps.inspector import NameInspector, MatchupInspector
from replay import Replay, is_replay, copy_replay
import datetime
import platform

#FolderProcessor
# @purpose - a singleton which traverses a directory tree, 
# organizes the replays using inspectors, and creates the proper subfolders.
class FolderProcessor:

    #folders - a hash for each subfolder created
    #same_series - a hash for temporarily storing replays that are in the same series
    #inspector - the inspector object that determines the key for folders hash
    #dest_folder - this is the target directory to write organized replays to

    def __init__(self, dest=''):
        self.__folders = {}
        self.__same_series = {}
        self.__inspector = None
        self.__dest_folder = dest
        self.__platform = platform.system()
        self.__rename_enabled = False

    #create_folders
    # @params - no parameters
    # @return - no return values
    # @purpose - creates the necessary subfolders from the folders hash where 
    #   each key is the folder name. Then, it copies all replays into 
    #   the appropriate locations
    def __create_folders(self):
        parent_folder = join(self.__dest_folder, 'Replays')
        #create parent directory is called "RepS"
        try:
            mkdir(parent_folder)
        except OSError:
            raise Exception('Replays folder is already formed')

        #for each key of hash, create the folder name
        #and copy the necessary replays into it
        for key in self.__folders:
            folder = join(parent_folder, key)
            try:
                mkdir(folder)
            except OSError:
                pass

            #copy replays into new folder
            for replay in self.__folders[key]:
                cp(replay.local_path, folder)

                #only rename replays if enabled
                if self.__rename_enabled:
                    #give the replays a more descriptive name
                    old_name = ''
                    if self.__platform is 'Windows':
                        old_name = join(folder, replay.local_path.split('\\')[-1])
                    else:
                        old_name = join(folder, replay.local_path.split('/')[-1])

                    #only assign numbers if there are more than one copy of replays
                    #with the same players in a 1v1 match
                    if replay.series_flag > -1:
                        temp = replay.replay_name.split('.')[0]
                        temp = temp + (' (%d)' % (replay.series_flag+1)) + '.SC2Replay'
                        replay.replay_name = temp

                    new_name = join(folder, replay.replay_name)
                    rename(old_name, new_name)
                
    #depth_first_search
    # @params - the path to start the search and a temporary intermediate path used to
    #   keep track of the current working directory
    # @return - no return values
    # @purpose - recurssively search the folder structure for all SC2 replays and call
    #   the inspector to form add replays to the nececessary subfolders
    def __depth_first_search(self, start_path, inter_path):
        current_path = join(start_path, inter_path)
        dirs_and_files = listdir(current_path)
        dirs = []
        files = []

        for df in dirs_and_files:
            # print(current_path)

            if is_replay(join(current_path, df)):
                files.append(df)

            if isdir(join(current_path, df)):
                if 'Replays' == df:
                    raise Exception('Replays folder is already formed')
                else:
                    dirs.append(df)

        for i in range(len(dirs)):
            inter = join(inter_path, dirs[i])
            # print('recurse', inter)
            self.__depth_first_search(start_path, inter)


        
        key = ''
        #finished recursive steps, now we read the discovered replays
        for i in range(len(files)):

            src_file = join(start_path, inter_path, files[i])
            original = Replay(src_file)
            keys = self.__inspector.inspect(original)
            
            #go through each key
            for j in range(len(keys)):
                replay = copy_replay(original)
                key = keys[j]

                #place replays in proper folders
                if key in self.__folders.keys():
                    self.__folders[key].append(replay)

                else:
                    self.__folders[key] = []

                    #series flag -1 means there are no replay with the same player names, yet ...
                    replay.series_flag = -1
                    self.__folders[key].append(replay)


    #sort_chronologically
    # @params - no parameters
    # @return - no return values
    # @purpose - go through each replay in each folder and sort the list
    #   in chronological order using the UTC timestamp
    def __sort_chronogolocally(self):

        #the function to sort each
        by_UTC = lambda rep: rep.UTC_timestamp

        for key in self.__folders:
            self.__folders[key].sort(key=by_UTC)
                

    #mark_series
    # @params - no parameters
    # @return - no return values
    # @purpose - iterate through each replay in each folder and flag games
    #   in the same series
    def __mark_series(self):

        for key in self.__folders:

            for replay in self.__folders[key]:

                #place replays in proper folders
                if key in self.__same_series.keys():

                    count = self.__same_series[key].count(replay.replay_name)
                    if count > 0:
                        replay.series_flag = count

                    #if series flag is 1, then this is the first duplicate replay_name
                    #and we need to make the flag for the first replay flag as 0
                    if replay.series_flag == 1:
                        i = self.__same_series[key].index(replay.replay_name)
                        self.__folders[key][i].series_flag = 0

                    self.__same_series[key].append(replay.replay_name)

                else:
                    self.__same_series[key] = []
                    self.__same_series[key].append(replay.replay_name)

    #organize_replays
    # @params - the relative path to the folder of replays to search and
    #   the type of sort to conduct, either by matchup or by player
    #   with repay renaming set to false by default
    # @return - no return values
    # @purpose - organize all the replays in a given folder of SC2 replays.
    def organize_replays(self, folder_path, sortop, enable_rename=False):
        
        if (folder_path is None) or (folder_path is ''):
            raise Exception('folder_path must be defined and non-empty')
        
        if (sortop is None) or (sortop not in ('p', 'm')):
            raise Exception('sortop must be either {p|m}')

        if type(enable_rename) is not bool:
            raise Exception('enable_rename must be type bool')

        #form the proper inspector
        if sortop is 'p':
            self.__inspector = NameInspector()
        else:
            self.__inspector = MatchupInspector()

        #set file rename config
        self.__rename_enabled = enable_rename
                
        #perform depth first search for replays
        self.__depth_first_search(folder_path, '')

        #only sort chronologically if rename is enabled
        if self.__rename_enabled:
            #sort each replay in each folder chronologically
            self.__sort_chronogolocally()

            #mark replays with series tag if applicable
            self.__mark_series()

        #create the necessary subfolders
        self.__create_folders()
