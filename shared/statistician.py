'''
Created on Jan 21, 2013

@author: jhwan

'''
import math

minWindowSize = 300
maxWindowSize = 1000

class Statistician:
    def __init__(self, numHands):
        self.numLevels = 10
        self.initWindowSize = 30
        # window size is always between 300 and 1000
        self.windowSize = min(maxWindowSize, max(minWindowSize, numHands/10))
        
        #preflop
        self.SBNumFirstRounds = 0 #the total number of first rounds played so far from SB position 
        self.SBNumFirstRaises = 0 #the total number of first raises by opp from SB position
        self.SBRaiseMatrix = [[], []] #opp's raise amounts from the previous self.windowSize rounds (organized by round type)
        self.BBNumFirstRounds = 0
        self.BBNumFirstRaises = 0
        self.BBRaiseMatrix = [[], []]
    
    def processHand(self, oppName, button, hand):
        street = 0
        raiseRound = 0
        
        for i in range(2, len(hand)): #skipping the first two POST actions
            action = hand[i]
            
            if action[0] == "DEAL": #start of next street
                street += 1
                raiseRound = 0
            elif action[0] in ["SHOW", "REFUND", "WIN"]: #the end of the hand
                self.processEnd(button)
            elif action[-1] == oppName:
                self.processStreet(street, raiseRound, button, action)            
                raiseRound += 1
                
    def getPreflopDist(self, button, raiseRound, oppAction):
        oppRange = self.getPreflopRange(button, raiseRound, oppAction)
        oppLevels = self.fromRangeToLevels(oppRange)
        return self.fromLevelsToDist(oppLevels, numLevels = self.numLevels)

    def getPreflopRange(self, button, raiseRound, oppAction):
        raiseAmount = self.getRaiseAmount(oppAction)
        
        if button:
            return self.getSBPreflopRange(raiseRound, raiseAmount)
        else:
            return self.getBBPreflopRange(raiseRound, raiseAmount)

    # recording sub-methods
    def processStreet(self, street, raiseRound, button, oppAction):
        if street == 0 and raiseRound < 2: #pre-flop
            self.processPreflopStats(button, raiseRound, oppAction)
        elif street == 1: #flop
            self.processFlopStats(button, raiseRound, oppAction)
        elif street == 2: #turn
            self.processTurnStats(button, raiseRound, oppAction)
        else: #river
            self.processRiverStats(button, raiseRound, oppAction)
    
    def processEnd(self, button):
        pass
    
    def processPreflopStats(self, button, raiseRound, oppAction):
        if button:
            self.updateSBPreflopStats(raiseRound, oppAction)
        else:
            self.updateBBPreflopStats(raiseRound, oppAction)

    def processFlopStats(self, button, raiseRound, oppAction):
        pass
    
    def processTurnStats(self, button, raiseRound, oppAction):
        pass
    
    def processRiverStats(self, button, raiseRound, oppAction):
        pass

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
        elif action[0] == "RAISE" or action[0] == "BET":
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
                if num > arrayCopy[i]:
                    numBigger = i
                    break
            numBigger = len(arrayCopy)-1
        else:
            numBigger = arrayCopy.index(num)
            
        return [float(numBigger)/len(array), float(numBigger+numAppearances)/len(array)]
    
    # approximating the interval
    def fromRangeToLevels(self, oppRange, numLevels = 10):
        [a, b] = [oppRange[0]*numLevels, oppRange[1]*numLevels] 
        a1 = int(round(a))
        b1 = int(round(b))
        
        if a1 == b1:
            if a1 <= a and b1 <= b:
                return [a1, b1+1]
            elif a1 >= a and b1 >= b:
                return [a1-1, b1]
            else:
                return [a1-1, b1+1]
        else:
            return [a1, b1]
    
# expanding the interval    
#    def fromRangeToLevels(self, oppRange, numLevels = 10):
#        [a, b] = oppRange
#        a = int(math.floor(numLevels*a))
#        b = int(math.ceil(numLevels*b))
#        
#        if a == b:
#            return [a, b+1]
#        else:
#            return [a, b]
    
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
    pass

#    #check self.windowSize
#    stat1 = Statistician(1000)
#    print str(stat1.windowSize) + "?=300"
#    stat2 = Statistician(3000)
#    print str(stat2.windowSize) + "?=300"    
#    stat3 = Statistician(10000)
#    print str(stat3.windowSize) + "?=1000"    
#    stat4 = Statistician(25000)
#    print str(stat4.windowSize) + "?=1000"        
#    stat5 = Statistician(100000)
#    print str(stat5.windowSize) + "?=1000"        

#    stat = Statistician(1000)
#    levels = [[0, 10], [0, 5], [5, 10], [2, 7]]
#    for level in levels:
#        print stat.fromLevelsToDist(level)
        
#    arrays = [[12, 32, 90, 9, 3, 23, 100, 43, 98, 100],
#              [12, 33, 33, 33,3, 23, 100, 43, 98, 100],
#              [12, 33, 90, 9, 3, 23, 100, 43, 98, 100]]
#    for array in arrays:
#        oppRange = stat.compareNumToArray(33, array)
#        print stat.fromRangeToLevels(oppRange, numLevels = 5)

#    ranges = [[0.02, 0.03],[0.56, 0.62],[0.96, 0.98]]
#    for oppRange in ranges:
#        level = stat.fromRangeToLevels(oppRange)
#        print level
