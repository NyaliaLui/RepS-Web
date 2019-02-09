#Matchup Inspector - the inspector which is only concerned with
#the 1v1 matchup of a replay.
class MatchupInspector:

    def __init__(self):
        pass

    #sort - sort a list using simple sorting procedure
    def __sort(self, races):
        is_sorted = False
        swaps = 0
        temp = ''

        while(not is_sorted):
            for i in range(len(races)-1):

                if races[i] > races[i+1]:
                    temp = races[i]
                    races[i] = races[i+1]
                    races[i+1] = temp
                    swaps = swaps + 1

            is_sorted = (swaps == 0)
            swaps = 0
    

    #inspect - return the matchup seen in 
    #in this replay
    def inspect(self, replay):
        races = []
        
        for player in replay.players:
            races.append(player['race'])

        #we sort so matchups such as PvT and TvP
        #will be considered in the same folder
        self.__sort(races)

        matchup = ''
        for race in races:
            matchup = matchup + race + ' vs '

        #remove the last ' vs '
        matchup = matchup[:-4]

        return [matchup]
