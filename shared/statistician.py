'''
Created on Jan 21, 2013

@author: jhwan

'''
import math

class Statistician:
    def __init__(self):
        self.numLevels = 10
        self.initWindowSize = 30
        self.windowSize = 1000 #must be a multiple of 10
        self.oppRange = [0, 1]
        
        #preflop
        self.SBNumFirstRounds = 0 #the total number of first rounds played so far from SB position 
        self.SBNumFirstRaises = 0 #the total number of first raises by opp from SB position
        self.SBRaiseMatrix = [[], []] #opp's raise amounts from the previous self.windowSize rounds (organized by round type)
        self.BBNumFirstRounds = 0
        self.BBNumFirstRaises = 0
        self.BBRaiseMatrix = [[], []]
    
    def processHandHist(self, oppName, button, recentActions):
        street = 0
        raiseRound = 0
        
        for action in recentActions:
            if action[-1] == oppName:
                if street == 0 and raiseRound < 2:
                    self.processOppRaiseStats(button, raiseRound, action)
                else: #stats for other streets and preflop raises after two rounds
                    pass
                raiseRound += 1
            elif action[0] == "DEAL":
                street += 1
                raiseRound = 0

    def getPreflopDist(self, dealer, raiseRound, oppAction):
        oppRange = self.getPreflopRange(dealer, raiseRound, oppAction)
        oppLevels = self.fromRangeToLevels(oppRange)
        return self.fromLevelsToDist(oppLevels, numLevels = self.numLevels)

    def getPreflopRange(self, dealer, raiseRound, oppAction):
        raiseAmount = self.getRaiseAmount(oppAction)
        
        if dealer:
            return self.getSBPreflopRange(raiseRound, raiseAmount)
        else:
            return self.getBBPreflopRange(raiseRound, raiseAmount)

    # recording sub-methods
    def processOppRaiseStats(self, dealer, raiseRound, oppAction):
        if dealer:
            self.updateSBPreflopStats(raiseRound, oppAction)
        else:
            self.updateBBPreflopStats(raiseRound, oppAction)

    def updateSBPreflopStats(self, raiseRound, oppAction):
        if raiseRound == 0:
            self.SBNumFirstRounds += 1
            if oppAction[0] == "RAISE":
                self.SBNumFirstRaises += 1
                
        raiseAmount = self.getRaiseAmount(oppAction)
        self.SBRaiseMatrix[raiseRound].append(raiseAmount)
        # if the size of the list is too big
        if len(self.SBRaiseMatrix[raiseRound]) > self.windowSize:
            self.SBRaiseMatrix[raiseRound].pop(0)
                
    def updateBBPreflopStats(self, raiseRound, oppAction):
        if raiseRound == 0:
            self.BBNumFirstRounds += 1
            if oppAction[0] == "RAISE":
                self.BBNumFirstRaises += 1
                
        raiseAmount = self.getRaiseAmount(oppAction)
        self.BBRaiseMatrix[raiseRound].append(raiseAmount)
        # if the size of the list is too big
        if len(self.BBRaiseMatrix[raiseRound]) > self.windowSize:
            self.BBRaiseMatrix[raiseRound].pop(0)    

    # ranging sub-methods    
    def getSBPreflopRange(self, raiseRound, raiseAmount):
        # if we don't have enough cases
        if len(self.SBRaiseMatrix[raiseRound]) < self.initWindowSize:
            if raiseRound == 0:
                if raiseAmount == -1:
                    return [0.5,1]
                elif raiseAmount == 0:
                    return [0.2,0.5]
                else:
                    return [0,0.2]
                    
            if raiseRound == 1:
                if raiseAmount == -1:
                    return [0.1,0.2]
                elif raiseAmount == 0:
                    return [0.05,0.1]
                else:
                    return [0,0.05]
        else:
            oppRange = self.compareNumToArray(raiseAmount, self.SBRaiseMatrix[raiseRound])
                    
            if raiseRound == 1:
                raisePercentage = float(self.SBNumFirstRaises) / self.SBNumFirstRounds
                self.refineOppRange(raisePercentage, oppRange)
                
            return oppRange
                    
    def getBBPreflopRange(self, raiseRound, raiseAmount):
        if len(self.BBRaiseMatrix[raiseRound]) < self.initWindowSize:
            if raiseRound == 0:
                if raiseAmount == -1:
                    return [0.9,1]
                elif raiseAmount == 0:
                    return [0.6,0.9]
                else:
                    return [0,0.6]
                    
            if raiseRound == 1:
                if raiseAmount == -1:
                    return [0.5,0.6]
                elif raiseAmount == 0:
                    return [0.1,0.5]
                else:
                    return [0,0.1]
        else:
            oppRange = self.compareNumToArray(raiseAmount, self.BBRaiseMatrix[raiseRound])
                    
            if raiseRound == 1:
                raisePercentage = float(self.BBNumFirstRaises) / self.BBNumFirstRounds
                self.refineOppRange(raisePercentage, oppRange)
                
            return oppRange    
        
    # other helper sub-methods    
    # action is an array whose first element is its type, e.g. ['RAISE', 7, 'P1']
    def getRaiseAmount(self, action):
        if action[0] == "FOLD":
            return -1
        elif action[0] == "CALL":
            return 0
        elif action[0] == "RAISE":
            return action[1]
    
    def refineOppRange(self, percentage, oppRange):
        [a, b] = oppRange
        delta = (b - a) * percentage
        
        return [a, a + delta]
    
    def compareNumToArray(self, num, array):
        arrayCopy = list(array)
        arrayCopy.sort()
        arrayCopy.reverse()
        
        numBigger = None
        numAppearances = arrayCopy.count(num)
        
        if numAppearances == 0:
            for i in range(len(arrayCopy)):
                if arrayCopy[i] < num:
                    numBigger = i
                    break
        else:
            numBigger = arrayCopy.index(num)
                
        return [float(numBigger)/len(array), float(numBigger+numAppearances)/len(array)]
    
    def fromRangeToLevels(self, oppRange, numLevels = 10):
        [a, b] = oppRange
        a = int(math.floor(numLevels*a))
        b = int(math.ceil(numLevels*b))
        
        if a == b:
            return [a, b+1]
        else:
            return [a, b]
    
    def fromLevelsToDist(self, levels, numLevels = 10):
        lowerBound = numLevels - levels[1]
        upperBound = numLevels - levels[0]
        
        levelArray = range(numLevels)                
        for i in levelArray:
            if i >= lowerBound and i < upperBound:
                levelArray[i] = 1
            else:
                levelArray[i] = 0
        return levelArray                          
                                 
if __name__ == "__main__":
    stat = Statistician()

#    levels = [[0, 10], [0, 5], [5, 10], [2, 7]]
#    for level in levels:
#        print stat.fromLevelsToDist(level)
        
#    arrays = [[12, 32, 90, 9, 3, 23, 100, 43, 98, 100],
#              [12, 33, 33, 33,3, 23, 100, 43, 98, 100],
#              [12, 33, 90, 9, 3, 23, 100, 43, 98, 100]]
#    for array in arrays:
#        oppRange = stat.compareNumToArray(33, array)
#        print stat.fromRangeToLevels(oppRange, numLevels = 5)
