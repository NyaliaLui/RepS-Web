#Matchup Inspector
# @purpose - the inspector which is only concerned with
#the 1v1 matchup of a replay.
class MatchupInspector:

    def __init__(self):
        pass

    #sort
    # @params - a list of SC2 races
    # @return - no return values
    # @purpose - sort a list of SC2 races using bubble sort
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
    

    #inspect
    # @params - a SC2 replay
    # @return - the matchup seen in the given replay
    # @purpose - inspect a replay for the SC2 matchup that was played
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
