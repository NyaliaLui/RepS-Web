import unittest
from ..archiver import ZipArchiver, RARArchiver
import os
from shutil import rmtree

class ArchiverTestCase(unittest.TestCase):
    def test_zip_archiver(self):
        zipper = ZipArchiver()

        archive_file = os.path.join('uploads', 'Sample-Archive.zip')

        zipper.extract(archive_file, 'replays')

        files = os.listdir(os.path.join('replays', 'HasDuplicates'))
        self.assertTrue(len(files) == 7)

        zipper.create('TestArchive1.zip', 'HasDuplicates')

        rmtree(os.path.join('replays', 'HasDuplicates'))
        #this os remove is a test itself, cause if the archive doesn't exist
        #then an exception will be thrown
        os.remove('TestArchive1.zip')

    def test_rar_archiver(self):
        rarer = RARArchiver()
        
        archive_file = os.path.join('uploads', 'SampleReplays.rar')

        rarer.extract(archive_file, 'replays')

        directory = os.listdir('replays')
        self.assertTrue(len(directory) == 5)

        rarer.create('TestArchive2.rar', 'replays')

        #this os remove is a test itself, cause if the archive doesn't exist
        #then an exception will be thrown
        for i in range(5):
            os.remove(os.path.join('replays', directory[i]))

        os.remove('TestArchive2.rar')
