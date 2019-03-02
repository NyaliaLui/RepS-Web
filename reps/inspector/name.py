#Name Inspector
# @purpose - the inspector which is only concerned with
#the list of names in the given replay.
class NameInspector:

    def __init__(self):
        pass


    #inspect
    # @params - a SC2 replay
    # @return - the list of names seen in the given replay
    # @purpose - inspect a replay for the list of player names
    def inspect(self, replay):
        names = []
        for player in replay.players:
            names.append(player['clan_tag'] + ' ' + player['name'])

        return names