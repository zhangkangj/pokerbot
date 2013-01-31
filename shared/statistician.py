'''
Created on Jan 21, 2013

@author: jhwan

'''
from calculator import Calculator
from shared.pbots_calc import calc

#fixed prior distributions
SBPreflop = [
             [[0.5,1], [0.2,0.5], [0,0.2]],
             [[0.9,1], [0.6,0.9], [0,0.6]]             
             ]
BBPreflop = [
             [[0.9,1], [0.6,0.9], [0,0.6]],
             [[0.5,1], [0.2,0.5], [0,0.2]]
             ]
SBFlop = [
          [[0.9,1], [0.6,0.9], [0,0.6]],
          [[0.5,1], [0.2,0.5], [0,0.2]]
          ]
BBFlop = [
          [[0.5,1], [0.2,0.5], [0,0.2]],
          [[0.9,1], [0.6,0.9], [0,0.6]]          
          ]
SBTurn = [
          [[0.9,1], [0.6,0.9], [0,0.6]],
          [[0.5,1], [0.2,0.5], [0,0.2]]
          ]
BBTurn = [
          [[0.5,1], [0.2,0.5], [0,0.2]],
          [[0.9,1], [0.6,0.9], [0,0.6]]          
          ]
SBRiver = [
           [[0.9,1], [0.6,0.9], [0,0.6]],
           [[0.5,1], [0.2,0.5], [0,0.2]]
           ]
BBRiver = [
           [[0.5,1], [0.2,0.5], [0,0.2]],
           [[0.9,1], [0.6,0.9], [0,0.6]]           
           ]
SBPriors = [SBPreflop, SBFlop, SBTurn, SBRiver]
BBPriors = [BBPreflop, BBFlop, BBTurn, BBRiver]


class Statistician:
    def __init__(self):
        self.cal = Calculator()
        self.numLevels = 10
        self.initWindowSize = 30
        # window size is always between 300 and 1000
        self.windowSize = 100
        self.boardCards = []
        self.oppRange = [0, 1]
        
        self.SBStats = [
                        [[], []], #preflop (which has two raise rounds by default)
                        [[], []], #flop
                        [[], []], #turn
                        [[], []]  #river
                        ]
        self.SBStatsSorted = [[[], []], [[], []], [[], []], [[], []]]
        self.BBStats = [[[], []], [[], []], [[], []], [[], []]]
        self.BBStatsSorted = [[[], []], [[], []], [[], []], [[], []]]
        
        self.oppShowdownPreflopEqu = []
        self.oppShowdownTurnEqu = []
        self.oppShowdownRiverEqu = []
        self.oppShowdowns = []
        self.oppShowdownWins = []
        self.myFolds = []
        self.oppFolds = []
        
        self.raiseHistSorted = None
            
    def processHand(self, oppName, myName, button, hand):
        street = 0
        raiseRound = 0
        showdown = False
        folding = False
        oppFolding = False
        
        for i in range(2, len(hand)): #skipping the first two POST actions
            action = hand[i]
            
            if action[0] == "DEAL": #start of next street
                street += 1
                raiseRound = 0
            elif action[-1] == myName and action[0] == "FOLD":
                folding = True
            elif action[-1] == oppName:
                if action[0] == "SHOW":
                    showdown = True
                    self.processShowdown([action[1], action[2]], hand[-1], oppName)
                elif action[0] == "FOLD":
                    oppFolding = True
                else:
                    self.processStreetAction(button, action, street, raiseRound)            
                    raiseRound += 1
                    
        if showdown:
            self.addNewEntry(self.oppShowdowns, True)
        else:
            self.addNewEntry(self.oppShowdowns, False)
            
        if folding:
            self.addNewEntry(self.myFolds, True)
        else:
            self.addNewEntry(self.myFolds, False)
            
        if oppFolding:
            self.addNewEntry(self.oppFolds, True)
        else:
            self.addNewEntry(self.oppFolds, False)
                
    def getOppDist(self, button, oppAction, street, raiseRound):
        if raiseRound > 1:
            return None
   
        oppRange = self.getStreetRange(button, oppAction, street, raiseRound)      
        oppLevels = self.fromRangeToLevels(oppRange)
        oppDist = self.fromLevelsToDist(oppLevels, numLevels = self.numLevels)
        
        if self.hasEnoughHistory(self.raiseHistSorted):
            oppDist = self.smoothDist(oppDist, sortedArray = self.raiseHistSorted)
        else:
            oppDist = self.smoothDist(oppDist)
            
        return oppDist

    def getOppShowdownEqu(self, street):
        if street == "PREFLOP":
            if self.oppShowdownPreflopEqu == []:
                return 0.5
            return float(sum(self.oppShowdownPreflopEqu))/len(self.oppShowdownPreflopEqu)
        elif street == "TURN":
            if self.oppShowdownTurnEqu == []:
                return 0.5
            return float(sum(self.oppShowdownTurnEqu))/len(self.oppShowdownTurnEqu)
        elif street == "RIVER":
            if self.oppShowdownRiverEqu == []:
                return 0.5            
            return float(sum(self.oppShowdownRiverEqu))/len(self.oppShowdownRiverEqu)
            
    def getOppShowdownRate(self):
        if self.oppShowdowns == []:
            return 1
        
        return float(sum(self.oppShowdowns)) / len(self.oppShowdowns)

    def getOppShowdownWinRate(self):
        if self.oppShowdownWins == []:
            return 0
        
        return float(sum(self.oppShowdownWins)) / len(self.oppShowdownWins)
    
    def getMyFoldingRate(self):
        if self.myFolds == []:
            return None
        
        return float(sum(self.myFolds)) / len(self.myFolds)

    def getOppFoldingRate(self):
        if self.oppFolds == []:
            return None
        
        return float(sum(self.oppFolds)) / len(self.oppFolds)

    def getBoardCards(self, boardCards):
        self.boardCards = boardCards

    def hasEnoughHistory(self, history):
        if len(history) < self.initWindowSize:
            return False
        else:
            return True

    def getSortedArray(self, button, street, raiseRound):
        if button:
            return self.SBStatsSorted[street][raiseRound]
        else:
            return self.BBStatsSorted[street][raiseRound]

    def getStreetRange(self, button, oppAction, street, raiseRound):
        if button:
            if street == 0: #if in pre-flop, SB always query opp's action from previous raise round.
                raiseRound = raiseRound - 1            
            prior = SBPriors[street][raiseRound]
        else:
            prior = BBPriors[street][raiseRound]
            if street != 0: #if not in pre-flop, BB always query opp's action from previous raise round
                raiseRound = raiseRound - 1
            
        self.raiseHistSorted = self.getSortedArray(button, street, raiseRound)    
        raiseAmount = self.getRaiseAmount(oppAction)
        if raiseRound == 0:
            if not self.hasEnoughHistory(self.raiseHistSorted):
                if raiseAmount == -1:
                    self.range = prior[0]
                elif raiseAmount == 0:
                    self.range = prior[1]                
                else:
                    self.range = prior[2]                
            else:
#                print self.raiseHistSorted
                self.oppRange = self.compareNumToArray(raiseAmount, self.raiseHistSorted)
        else:
            if not self.hasEnoughHistory(self.raiseHistSorted):
                raisePercentage = float(prior[2][1] - prior[2][0])
            else:
                numAppearances = self.raiseHistSorted.count(raiseAmount)
                
                if numAppearances == 0:
                    numBigger = len(self.raiseHistSorted)-1
        
                    for i in range(len(self.raiseHistSorted)):
                        if raiseAmount > self.raiseHistSorted[i]:
                            numBigger = i
                            break
                else:
                    numBigger = self.raiseHistSorted.index(raiseAmount)
                        
                raisePercentage = float(numBigger + numAppearances) / len(self.raiseHistSorted)
#                raisePercentage = float(self.getNumPosElements(self.raiseHistSorted)) / len(self.raiseHistSorted)         
            
#            print str(oppAction) + "|" + str(street) + "|" + str(raiseRound) + "|" + str(raisePercentage)
#            print "pre-range: " + str(self.oppRange)
            self.oppRange = self.refineOppRange(raisePercentage, self.oppRange)
#            print "post-range: " + str(self.oppRange)
        return self.oppRange                
    
    def processStreetAction(self, button, oppAction, street, raiseRound):
        if raiseRound > 1:
            return
        
        raiseAmount = self.getRaiseAmount(oppAction)
        
        if button:
            raiseHist = self.SBStats[street][raiseRound]
        else:
            raiseHist = self.BBStats[street][raiseRound]
            
        self.addNewEntry(raiseHist, raiseAmount)
        
        if button:
            self.SBStatsSorted[street][raiseRound] = self.reverseSortArray(raiseHist)
        else:
            self.BBStatsSorted[street][raiseRound] = self.reverseSortArray(raiseHist)
            
    def processShowdown(self, oppHoleCards, result, oppName):
        if result[-1] == oppName:
            self.addNewEntry(self.oppShowdownWins, True)
        else:
            self.addNewEntry(self.oppShowdownWins, False)
                
        turnBoard = self.boardCards[0:4]
        oppTurnEqu = calc("".join(oppHoleCards) + ":xx", "".join(turnBoard), "", 3000).ev[0]   
        self.addNewEntry(self.oppShowdownTurnEqu, oppTurnEqu)     
            
        riverBoard = self.boardCards
        oppRiverEqu = calc("".join(oppHoleCards) + ":xx", "".join(riverBoard), "", 3000).ev[0]         
        self.addNewEntry(self.oppShowdownRiverEqu, oppRiverEqu)             
    
    def addNewEntry(self, history, newEntry):
        history.append(newEntry)
        if len(history) > self.windowSize:
            history.pop(0)
        
    
    # ranging sub-methods    
                            
    # other helper sub-methods    
    # action is an array whose first element is its type, e.g. ['RAISE', 7, 'P1']
    def getRaiseAmount(self, action):
        if action[0] == "FOLD":
            return -1
        elif action[0] == "CALL" or action[0] == "CHECK":
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
    # don't modify sortedArray
    def compareNumToArray(self, num, sortedArray):
        numBigger = None
        numAppearances = sortedArray.count(num)
        
        if numAppearances == 0:
            numBigger = len(sortedArray)-1

            for i in range(len(sortedArray)):
                if num > sortedArray[i]:
                    numBigger = i
                    break
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
    
    # don't modify sortedArray
    def smoothDist(self, dist, sortedArray = None):
        totalWeight = float(sum(dist))
        
        if sortedArray == None:
            dist1 = [totalWeight/self.numLevels]*self.numLevels
            return [(x+y) for (x,y) in zip(dist, dist1)]
        else:        
            numFolds = sortedArray.count(-1)
            numCalls = sortedArray.count(0)
            foldPercentage = numFolds/float(len(sortedArray))
            raisePercentage = 1 - (numFolds + numCalls)/float(len(sortedArray))
            
            foldLevels = int(round(foldPercentage*self.numLevels))
            raiseLevels = int(round(raisePercentage*self.numLevels))
            
            if foldLevels == self.numLevels:
                dist1 = [0]*self.numLevels
            else:   
                avgWeight1 = totalWeight / (self.numLevels - foldLevels)
                dist1 = [0]*foldLevels
                dist1.extend([avgWeight1]*(self.numLevels - foldLevels))
                
            if raiseLevels == 0:
                dist2 = [0]*self.numLevels
            else:
                avgWeight2 = totalWeight / raiseLevels
                dist2 = [0]*(self.numLevels - raiseLevels)
                dist2.extend([avgWeight2]*raiseLevels)
            
            return [(x+y+z) for (x, y, z) in zip(dist, dist1, dist2)]
        
if __name__ == "__main__":
    pass

    #check smoothing
#    stat = Statistician(1000)
#    dist = [0,0,0,1,1,1,1,0,0,0]
#    sortedArray = [1]*10 + [0]*10 + [-1]*10
#    print stat.smoothDist(dist, sortedArray)
    
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
