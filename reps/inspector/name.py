#Name Inspector - the inspector which is only concerned with
#the list of names in the given replay.
class NameInspector:

    def __init__(self):
        pass


    #inspect - return the list of names
    #seen in this replay
    def inspect(self, replay):
        names = []
        for player in replay.players:
            names.append(player['clan_tag'] + ' ' + player['name'])

        return names