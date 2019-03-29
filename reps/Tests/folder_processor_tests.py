import unittest
import os
from .. import FolderProcessor
from shutil import rmtree
import traceback

class FolderProcessorTestCase(unittest.TestCase):
    def setUp(self):
        self.root_path = 'SampleReplays'
        self.fp = FolderProcessor(dest=self.root_path)

    def test_sortby_matchup(self):
        self.fp.organize_replays(self.root_path, 'm')

        #Replays must be a directory
        self.assertTrue(os.path.isdir(os.path.join(self.root_path, 'Replays')))

        #the matchup folder must be a directory
        temp_path = os.path.join(self.root_path, 'Replays', 'Protoss vs Terran')
        self.assertTrue(os.path.isdir(temp_path))

        #all 4 sample files must be in the directory
        files = os.listdir(temp_path)
        self.assertTrue(len(files) == 5)

        #remove the directory for further testing
        rmtree(os.path.join(self.root_path, 'Replays'))

    def test_sortby_player(self):
        self.fp.organize_replays('SampleReplays', 'p')

        #Replays must be a directory
        replays_path = os.path.join(self.root_path, 'Replays')
        self.assertTrue(os.path.isdir(replays_path))

        #the player folders must be directories
        fs = os.listdir(replays_path)
        temp_path1 = os.path.join(replays_path, fs[0])
        temp_path2 = os.path.join(replays_path, fs[1])
        temp_path3 = os.path.join(replays_path, fs[2])
        temp_path4 = os.path.join(replays_path, fs[3])
        self.assertTrue(os.path.isdir(temp_path1))
        self.assertTrue(os.path.isdir(temp_path2))
        self.assertTrue(os.path.isdir(temp_path3))
        self.assertTrue(os.path.isdir(temp_path4))

        #both player folders must have all 4 sample replays
        files1 = os.listdir(temp_path1)
        files2 = os.listdir(temp_path2)
        files3 = os.listdir(temp_path3)
        files4 = os.listdir(temp_path4)
        self.assertTrue(len(files1) == 4 or len(files1) == 1)
        self.assertTrue(len(files2) == 4 or len(files2) == 1)
        self.assertTrue(len(files3) == 4 or len(files3) == 1)
        self.assertTrue(len(files4) == 4 or len(files4) == 1)

        #remove the directory for further testing
        rmtree(replays_path)

    def test_sort_twice(self):
        self.fp.organize_replays('SampleReplays', 'p')

        try:
            self.fp.organize_replays('SampleReplays', 'p')
        except Exception as ex:
            self.assertTrue('Replays folder is already formed' == str(ex))

        #remove the directory for further testing
        rmtree(os.path.join('SampleReplays', 'Replays'))

    def test_exceptions(self):
        try:
            self.fp.organize_replays('','m')
        except Exception as ex:
            self.assertTrue('folder_path must be defined and non-empty' == str(ex))

        try:
            self.fp.organize_replays('bling','')
        except Exception as ex:
            self.assertTrue('sortop must be either {p|m}' == str(ex))

    def test_empty_collection(self):
        folder_root = 'EmptyFolder'
        os.mkdir(folder_root)

        another_fp = FolderProcessor(folder_root)
        another_fp.organize_replays(folder_root, 'p')

        temp_path = os.path.join(folder_root, 'Replays')
        self.assertTrue(os.path.isdir(temp_path))
        files = os.listdir(temp_path)
        self.assertTrue(len(files) == 0)

        rmtree(folder_root)

    def test_collection_with_duplicates(self):
        folder_root = 'HasDuplicates'
        another_fp = FolderProcessor(folder_root)
        another_fp.organize_replays(folder_root, 'm')

        replays_path = os.path.join(folder_root, 'Replays')        
        self.assertTrue(os.path.isdir(replays_path))

        #the matchup folder must be a directory
        temp_path = os.path.join(folder_root, 'Replays', 'Protoss vs Terran')        
        self.assertTrue(os.path.isdir(temp_path))

        #both player folders must have all 7 sample replays
        files = os.listdir(temp_path)
        self.assertTrue(len(files) == 7)

        #remove the directory for further testing
        rmtree(replays_path)

    def test_sort_with_renaming(self):
        self.fp.organize_replays('SampleReplays', 'p', True)

        #Replays must be a directory
        replays_path = os.path.join(self.root_path, 'Replays')
        self.assertTrue(os.path.isdir(replays_path))

        #the player folders must be directories
        fs = os.listdir(replays_path)
        temp_path1 = os.path.join(replays_path, fs[0])
        temp_path2 = os.path.join(replays_path, fs[1])
        temp_path3 = os.path.join(replays_path, fs[2])
        temp_path4 = os.path.join(replays_path, fs[3])
        self.assertTrue(os.path.isdir(temp_path1))
        self.assertTrue(os.path.isdir(temp_path2))
        self.assertTrue(os.path.isdir(temp_path3))
        self.assertTrue(os.path.isdir(temp_path4))

        #both player folders must have all 4 sample replays
        files1 = os.listdir(temp_path1)
        files2 = os.listdir(temp_path2)
        files3 = os.listdir(temp_path3)
        files4 = os.listdir(temp_path4)
        self.assertTrue(len(files1) == 4 or len(files1) == 1)
        self.assertTrue(len(files2) == 4 or len(files2) == 1)
        self.assertTrue(len(files3) == 4 or len(files3) == 1)
        self.assertTrue(len(files4) == 4 or len(files4) == 1)

        #replays in both folders must have the new naming scheme
        #detected with the 'vs' substring
        for filename in files1:
            self.assertTrue('vs' in filename)

        for filename in files2:
            self.assertTrue('vs' in filename)

        for filename in files3:
            self.assertTrue('vs' in filename)

        for filename in files4:
            self.assertTrue('vs' in filename)

        #remove the directory for further testing
        rmtree(replays_path)
