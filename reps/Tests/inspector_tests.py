import unittest
from ..inspector import NameInspector, MatchupInspector
from .. import Replay
import platform

class InspectorTestCase(unittest.TestCase):
    def setUp(self):
        self.replay = None
        if platform.system() is 'Windows':
            self.replay = Replay('SampleReplays\\Sample 1.SC2Replay')
        else:
            self.replay = Replay('SampleReplays/Sample 1.SC2Replay')

        self.namer = NameInspector()
        self.matchupper = MatchupInspector()

    def test_name_inspector(self):
        names = self.namer.inspect(self.replay)
        self.assertTrue(names == ['[IxGeu] goblin', ' Clem'])

    def test_matchup_inspector(self):
        matchup = self.matchupper.inspect(self.replay)
        self.assertTrue('Protoss vs Terran' == matchup[0])