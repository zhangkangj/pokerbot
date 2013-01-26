'''
Created on Jan 21, 2013

@author: jhwan

'''
import math

minWindowSize = 300
maxWindowSize = 1000

#fixed prior distributions
SBPreflop = [
             [[0.5,1], [0.2,0.5], [0,0.2]]
             ]
BBPreflop = [
             [[0.9,1], [0.6,0.9], [0,0.6]],
             [[0.5,0.6], [0.1,0.5], [0,0.1]]
             ]
SBFlop = [
          [[0.9,1], [0.6,0.9], [0,0.6]],
          [[0.5,0.6], [0.1,0.5], [0,0.1]]
          ]
BBFlop = [
          [[0.9,1], [0.6,0.9], [0,0.6]],
          [[0.5,0.6], [0.1,0.5], [0,0.1]]
          ]
SBTurn = []
BBTurn = []
SBRiver = []
BBRiver = []
SBPriors = [SBPreflop, SBFlop, SBTurn, SBRiver]
BBPriors = [BBPreflop, BBFlop, BBTurn, BBRiver]


class Statistician:
    def __init__(self, numHands):
        self.numLevels = 10
        self.initWindowSize = 30
        # window size is always between 300 and 1000
        self.windowSize = min(maxWindowSize, max(minWindowSize, numHands/10))
        
        self.SBStats = [
                        [[], []], #preflop (which has two raise rounds by default)
                        [[], []], #flop
                        [[], []], #turn
                        [[], []]  #river
                        ]
        self.SBStatsSorted = [[[], []], [[], []], [[], []], [[], []]]
        self.BBStats = [[[], []], [[], []], [[], []], [[], []]]
        self.BBStatsSorted = [[[], []], [[], []], [[], []], [[], []]]
            
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
                self.processStreetAction(button, action, street, raiseRound)            
                raiseRound += 1
                
    def getOppDist(self, button, oppAction, street, raiseRound):   
        oppRange = self.getStreetRange(button, oppAction, street, raiseRound)             
        oppLevels = self.fromRangeToLevels(oppRange)
        return self.fromLevelsToDist(oppLevels, numLevels = self.numLevels)

    def getStreetRange(self, button, oppAction, street, raiseRound):
        if button:
            streetRaiseHistSorted = self.SBStatsSorted[street]
            prior = SBPriors[street][raiseRound]
        else:
            streetRaiseHistSorted = self.BBStatsSorted[street]            
            prior = BBPriors[street][raiseRound]

        raiseAmount = self.getRaiseAmount(oppAction)
        raiseHistSorted = streetRaiseHistSorted[raiseRound]
        if len(raiseHistSorted) < self.initWindowSize:
            if raiseAmount == -1:
                return prior[0]
            elif raiseAmount == 0:
                return prior[1]                
            else:
                return prior[2]                
        else:           
            oppRange = self.compareNumToArray(raiseAmount, raiseHistSorted)

            if raiseRound != 0:
                prevRaiseHistSorted = streetRaiseHistSorted[raiseRound-1]
                raisePercentage = float(self.getNumPosElements(prevRaiseHistSorted)) / len(prevRaiseHistSorted)
                self.refineOppRange(raisePercentage, oppRange)
            
            return oppRange                
    
    def processStreetAction(self, button, oppAction, street, raiseRound):
        raiseAmount = self.getRaiseAmount(oppAction)
        
        if button:
            raiseHist = self.SBStats[street][raiseRound]
            raiseHistSorted = self.SBStatsSorted[street][raiseRound]
        else:
            raiseHist = self.BBStats[street][raiseRound]
            raiseHistSorted = self.BBStatsSorted[street][raiseRound]
        
        raiseHist.append(raiseAmount)
        if len(raiseHist) > self.windowSize:
            raiseHist.pop(0)
            
        raiseHistSorted = self.reverseSortArray(raiseHist)
            
    def processEnd(self, button):
        pass
    
    # ranging sub-methods    
                            
    # other helper sub-methods    
    # action is an array whose first element is its type, e.g. ['RAISE', 7, 'P1']
    def getRaiseAmount(self, action):
        if action[0] == "FOLD":
            return -1
        elif action[0] == "CALL":
            return 0
        elif action[0] == "RAISE" or action[0] == "BET":
            return action[1]
    
    # 1. array contains only positive numbers, 0 or -1
    # 2. array is sorted from high to low
    def getNumPosElements(self, array):
        numZeros = array.count(0)
        
        if numZeros == 0:
            numNeg = array.count(-1)
            if numNeg == 0:
                return len(array)
            else:
                return array.index(-1)
        else:
            return array.index(0)
    
    def refineOppRange(self, percentage, oppRange):
        [a, b] = oppRange
        delta = (b - a) * percentage
        
        return [a, a + delta]
    
    def reverseSortArray(self, array):
        arraySorted = list(array)
        arraySorted.sort()
        arraySorted.reverse()
        
        return arraySorted
    
    #sortedArray is sorted from high to low
    def compareNumToArray(self, num, sortedArray):
        numBigger = None
        numAppearances = sortedArray.count(num)
        
        if numAppearances == 0:
            for i in range(len(sortedArray)):
                if num > sortedArray[i]:
                    numBigger = i
                    break
            numBigger = len(sortedArray)-1
        else:
            numBigger = sortedArray.index(num)
            
        return [float(numBigger)/len(sortedArray), float(numBigger+numAppearances)/len(sortedArray)]
    
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
