import unittest
import os
from .. import Dispatcher
from shutil import move, rmtree
import traceback

class DispatcherTestCase(unittest.TestCase):
    def setUp(self):
        self.root_path = 'C:\Users\Nyalia Lui\Documents\GitHub\RepS'
        self.sample_archive = 'Sample-Archive.zip'
        self._upload_folder = os.path.join(self.root_path, 'uploads')
        self._replay_folder = os.path.join(self.root_path, 'replays')
        self.manager = Dispatcher(self.root_path)

    def test_sortby_matchup(self):
        name = self.manager.dispatch(self.sample_archive, 'm')
        self.assertTrue('syalper-' == name[:-1])
        self.assertTrue(name[-1:].isdigit())

        #rename the zip archive and remove inside replays for futher testing
        oldzip = os.path.join(self._upload_folder, name+'.zip')
        newzip = os.path.join(self._upload_folder, self.sample_archive)
        move(oldzip, newzip)

        rmtree(os.path.join(self._replay_folder, name))

    def test_sortby_player(self):
        name = self.manager.dispatch(self.sample_archive, 'p')
        self.assertTrue('syalper-' == name[:-1])
        self.assertTrue(name[-1:].isdigit())

        #rename the zip archive and remove inside replays for futher testing
        oldzip = os.path.join(self._upload_folder, name+'.zip')
        newzip = os.path.join(self._upload_folder, self.sample_archive)
        move(oldzip, newzip)

        rmtree(os.path.join(self._replay_folder, name))
