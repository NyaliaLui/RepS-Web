import unittest
from .. import Replay
from ..replay import is_replay, copy_replay, create_player
import platform
import mpyq


class ReplayTestCase(unittest.TestCase):
    def setUp(self):
        self.replay_file = ''
        if platform.system() is 'Windows':
            self.replay_file = 'SampleReplays\\Sample 1.SC2Replay'
        else:
            self.replay_file = 'SampleReplays/Sample 1.SC2Replay'

    def test_is_replay(self):
        self.assertTrue(is_replay(self.replay_file))

    def test_create_player(self):
        player = create_player('noticals', 'Protoss', 'sc2')
        self.assertTrue(player['name'] == 'noticals')
        self.assertTrue(player['race'] == 'Protoss')
        self.assertTrue(player['clan_tag'] == 'sc2')
        self.assertTrue(player['team_id'] == 0)

    def test_empty_replay(self):
        empty = Replay()
        self.assertTrue(empty.archive is None)

    def test_sample_replay(self):
        replay = Replay(self.replay_file)
        self.assertTrue(len(replay.players) > 0)
        self.assertTrue(replay.series_flag == -1)
        self.assertTrue(isinstance(replay.archive, mpyq.MPQArchive))
        self.assertTrue(replay.baseBuild == 71663)
        self.assertTrue(replay.protocol is not None)
        self.assertTrue(isinstance(replay.details, dict))
        self.assertTrue(replay.local_path is self.replay_file)
        self.assertTrue('.SC2Replay' == replay.replay_name[-10:])
        self.assertTrue(replay.UTC_timestamp > 0)

    def test_copy_replay(self):
        replay = Replay(self.replay_file)
        copy = copy_replay(replay)

        self.assertTrue(copy.players == replay.players)
        self.assertTrue(copy.series_flag == replay.series_flag)
        self.assertTrue(isinstance(copy.archive, mpyq.MPQArchive))
        self.assertTrue(copy.baseBuild == replay.baseBuild)
        self.assertTrue(copy.protocol is not None)
        self.assertTrue(copy.details == replay.details)
        self.assertTrue(copy.local_path is replay.local_path)
        self.assertTrue(copy.replay_name is replay.replay_name)
        self.assertTrue(copy.UTC_timestamp == replay.UTC_timestamp)
