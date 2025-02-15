from s2protocol import versions
import mpyq
import sys
from os.path import isfile
from copy import deepcopy

#is_replay
# @params - relative path to the replay file
# @return - returns true if file is a replay
# @purpose - determine if a file is a SC2 replay
def is_replay(replay_path):
    ret = (isfile(replay_path) and ('.SC2Replay' in replay_path[-10:]))
    return ret

#create_player
# @params - the name, SC2 race, clan (optional), and team (optional) for a player
# @return - returns the SC2 player in JSON format
# @purpose - construct a SC2 player as JSON object
def create_player(name, race, clan='', team=0):
    return { 'name': name, 'race': race, 'clan_tag': clan, 'team_id': team }

#Replay
# @purpose - a wrapper around S2 protocol replay files
class Replay:

    #players - list of players. each player is a JSON object
        # {
        #    'name': players name,
        #    'race': one of three SC2 races,
        #    'clan_tag': clan name if applicable
        #    'team_id': which lobby team the player is on
        # }
    #series_flag - an incrementing flag to illustrate if the replay is in a series and which number in the series
    #               value of -1 means the replay is not in a series
    #archive - the mpyq archive of the replay
    #baseBuild - the base build of the replay according to s2protocol
    #header - the replay header information
    #protocol - the protocol for this replay
    #details - the list of details for this replay in JSON format
    #local_path - the relative path to the replay
    #replay_name - the human readable name given to the replay
    #UTC_timestamp - the replay timestamp in UTC time

    def __init__(self, replay_path = ''):
        self.players = []
        self.series_flag = -1
        self.archive = None
        self.baseBuild = None
        self.header = None
        self.protocol = None
        self.details = None
        self.local_path = replay_path
        self.replay_name = ''
        self.UTC_timestamp = 0

        if replay_path is not '':
            #generate MPQ archive
            self.archive = mpyq.MPQArchive(replay_path)
            
            #get the replays protocol version
            contents = self.archive.header['user_data_header']['content']
            self.header = versions.latest().decode_replay_header(contents)

            # The header's baseBuild determines which protocol to use
            #part of this code was modified from 
            #s2_cli.py @ https://github.com/Blizzard/s2protocol/tree/master/s2protocol
            self.baseBuild = self.header['m_version']['m_baseBuild']
            try:
                self.protocol = versions.build(self.baseBuild)
            except Exception, e:
                print >> sys.stderr, 'Unsupported base build: {0} ({1})'.format(self.baseBuild, str(e))
                sys.exit(1)

            #replay details
            contents = self.archive.read_file('replay.details')
            self.details = self.protocol.decode_replay_details(contents)
            self.UTC_timestamp = self.details['m_timeUTC']

            #pre process for matchup and names
            num_players = len(self.details['m_playerList'])
            for i in range(num_players):

                player = None

                name = self.details['m_playerList'][i]['m_name']
                race = self.details['m_playerList'][i]['m_race']
                clan = ''
                team = self.details['m_playerList'][i]['m_teamId']

                if name.find('&lt;') > -1:
                    info = self.__beautify_name(name)
                    clan = info[0]
                    name = info[1]

                player = create_player(name, race, clan, team)
                self.players.append(player)

                if clan is '':
                    self.replay_name = self.replay_name + name + ' vs '
                else:
                    self.replay_name = self.replay_name + clan + ' ' + name + ' vs '

            #must take last ' vs ' off and put proper exstension on
            self.replay_name = self.replay_name[:-4] + '.SC2Replay'



    #beautify_name
    # @params - the human readable name
    # @return - the clan tag and player name in an easier to read format
    # @purpose - SC2 Replays put HTML tags with player names, this function removes those characters.
    def __beautify_name(self, name):
        infos = name.split('<sp/>')
        infos[0] = infos[0].replace('&lt;', '')
        infos[0] = infos[0].replace('&gt;', '')
        infos[0] = '[' + infos[0] + ']'

        return infos

#copy_replay
# @params - the SC2 replay
# @return - a copy of the SC2 replay
# @purpose - create a duplicate copy of the given SC2 replay
def copy_replay(replay):
    duplicate = Replay()

    duplicate.series_flag = replay.series_flag
    duplicate.players = replay.players[:]
    duplicate.archive = deepcopy(replay.archive)
    duplicate.baseBuild = replay.baseBuild
    duplicate.header = deepcopy(replay.header)
    duplicate.protocol = replay.protocol
    duplicate.details = deepcopy(replay.details)
    duplicate.local_path = replay.local_path[:]
    duplicate.replay_name = replay.replay_name[:]
    duplicate.UTC_timestamp = replay.UTC_timestamp

    return duplicate
