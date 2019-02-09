from os import listdir, chdir, mkdir, rename
from os.path import isdir, join
from shutil import copy as cp
from reps.inspector import NameInspector, MatchupInspector
from replay import Replay, is_replay, copy_replay
import datetime
import platform

#FolderProcessor - a singleton which
#traverses a directory tree, organizes the replays using inspectors,
#and creates the proper subfolders
class FolderProcessor:

    def __init__(self, dest=''):
        self.__folders = {}
        self.__same_series = {}
        self.__inspector = None
        self.__dest_folder = dest
        self.__platform = platform.system()

    #create_folders - creates necessary subfolders from the hash of replays
    #where each key is the folder name. Then, it copies all replays into 
    #the appropriate locations
    def __create_folders(self):
        parent_folder = join(self.__dest_folder, 'Replays')
        #create parent directory is called "RepS"
        try:
            mkdir(parent_folder)
        except OSError:
            pass

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
                
    #depth_first_search - recurssively search the folder structure for all replays
    #call the inspector to form and add to necessary buckets after reading a replay
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


    #sort_chronologically - go through each replay in each folder (hash key) and sort the list
    #in chronological order using the UTC timestamp
    def __sort_chronogolocally(self):

        #the function to sort each
        by_UTC = lambda rep: rep.UTC_timestamp

        for key in self.__folders:
            self.__folders[key].sort(key=by_UTC)
                

    #mark_series - iterate through each replay in each folder (hash key) and flag
    #games in the same series
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

    #organize_replays - conduct a depth first search on the given replay folder
    #and organize the replays.
    def organize_replays(self, folder_path, sort_type):
        
        #form the proper inspector
        if sort_type is 'p':
            self.__inspector = NameInspector()
        else:
            self.__inspector = MatchupInspector()
        
        #perform depth first search for replays
        self.__depth_first_search(folder_path, '')

        #sort each replay in each folder chronologically
        self.__sort_chronogolocally()

        #mark replays with series tag if applicable
        self.__mark_series()

        #create the necessary subfolders
        self.__create_folders()