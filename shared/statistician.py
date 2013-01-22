'''
Created on Jan 21, 2013

@author: jhwan

'''
import math

class Statistician:
    def __init__(self):
        self.initWindowSize = 30
        self.windowSize = 100
        self.oppRange = [0, 1]
        self.oppBBFirstTotalTimes = 0
        self.oppBBFirstRaiseTimes = 0
        self.oppSBFirstTotalTimes = 0
        self.oppSBFirstRaiseTimes = 0
        self.oppBBRaiseMatrix = [[], []]
        self.oppSBRaiseMatrix = [[], []]
    
    def processHandHist(self, oppName, button, recentActions):
        pass
#        street = 0
#        raiseRound = 0
#        
#        for action in recentActions:
#            if action[-1] == oppName:
#                if street == 0 and raiseRound < 2:
#                    self.processOppRaiseStats(button, raiseRound, action)
#                else:
#                    pass
#                raiseRound += 1
#            elif action[0] == "DEAL":
#                street += 1
#                raiseRound = 0
    
    def getOppRange(self):
        oppRange = range(10)
        lowerBound = 10 - math.ceil(self.oppRange[1]*10)
        upperBound = 10 - math.floor(self.oppRange[0]*10)
        for i in oppRange:
            if i >= lowerBound and i < upperBound:
                oppRange[i] = 1
            else:
                oppRange[i] = 0
        return oppRange
    
    def processOppRaiseStats(self, dealer, raiseRound, oppAction):
        raiseRatio = None
        
        if dealer:
            if raiseRound == 0:
                self.oppBBFirstTotalTimes += 1
            
            if oppAction[0] == "FOLD":                                   
                raiseRatio = -1
            elif oppAction[0] == "CALL":
                raiseRatio = 0
            elif oppAction[0] == "RAISE" and raiseRound == 0:
                raiseRatio = oppAction[1]             
                self.oppBBFirstRaiseTimes += 1
            
            self.oppBBRaiseMatrix[raiseRound].append(raiseRatio)
            if len(self.oppBBRaiseMatrix[raiseRound]) > self.windowSize:
                self.oppBBRaiseMatrix[raiseRound].pop(0)            
            
            # if we don't have enough cases
            if len(self.oppBBRaiseMatrix[raiseRound]) < self.initWindowSize:
                if raiseRound == 0:
                    if oppAction[0] == "FOLD":
                        self.oppRange = [0.5,1]
                    elif oppAction[0] == "CALL":
                        self.oppRange = [0.2,0.5]
                    elif oppAction[0] == "RAISE":
                        self.oppRange = [0,0.2]
                        
                if raiseRound == 1:
                    if oppAction[0] =="FOLD":
                        self.oppRange = [0.1,0.2]
                    elif oppAction[0] == "CALL":
                        self.oppRange = [0.05,0.1]
                    elif oppAction[0] == "RAISE":
                        self.oppRange = [0,0.05]
            else:
                numLarger = 0
                numSmaller = 0
            
                for num in self.oppBBRaiseMatrix[raiseRound]:
                    if num > raiseRatio:
                        numLarger += 1
                    elif num < raiseRatio:
                        numSmaller += 1
                        
                if raiseRound == 0:
                    lowPercent = int(100 * float(numLarger) / len(self.oppBBRaiseMatrix[raiseRound]))
                    highPercent = int(100 * (1 - float(numSmaller) / len(self.oppBBRaiseMatrix[raiseRound])))
                elif raiseRound == 1:
                    print self.oppBBFirstTotalTimes
                    print len(self.oppBBRaiseMatrix[raiseRound])
                    lowPercent = int(100 * (float(self.oppBBFirstRaiseTimes) / self.oppBBFirstTotalTimes) * (float(numLarger) / len(self.oppBBRaiseMatrix[raiseRound])))
                    highPercent = int(100 * (float(self.oppBBFirstRaiseTimes) / self.oppBBFirstTotalTimes) * (1 - float(numSmaller) / len(self.oppBBRaiseMatrix[raiseRound])))
              
                if highPercent - lowPercent < 10:
                    highPercent = min(100, highPercent + (1 + 10 - (highPercent - lowPercent)) / 2)
                    lowPercent = max(0, lowPercent - (10 - (highPercent - lowPercent)) / 2)
                    
                self.oppRange = [float(lowPercent) / 100, float(highPercent) / 100]
        else:  
            if raiseRound == 0:
                self.oppSBFirstTotalTimes += 1
            
            if oppAction[0] == "FOLD":                                   
                raiseRatio = -1
            elif oppAction[0] == "CALL":
                raiseRatio = 0
            elif oppAction[0] == "RAISE" and raiseRound == 0:
                raiseRatio = oppAction[1]           
                self.oppSBFirstRaiseTimes += 1
                
            self.oppSBRaiseMatrix[raiseRound].append(raiseRatio)
            if len(self.oppSBRaiseMatrix[raiseRound]) > self.windowSize:
                self.oppSBRaiseMatrix[raiseRound].pop(0)                                
                
            if len(self.oppSBRaiseMatrix[raiseRound]) < self.initWindowSize:
                if raiseRound == 0:
                    if oppAction[0] == "FOLD":
                        self.oppRange = [0.9,1]
                    elif oppAction[0] == "CALL":
                        self.oppRange = [0.6,0.9]
                    elif oppAction[0] == "RAISE":
                        self.oppRange = [0,0.6]
                        
                if raiseRound == 1:
                    if oppAction[0] =="FOLD":
                        self.oppRange = [0.5,0.6]
                    elif oppAction[0] == "CALL":
                        self.oppRange = [0.1,0.5]
                    elif oppAction[0] == "RAISE":
                        self.oppRange = [0,0.1]
            else:
                numLarger = 0
                numSmaller = 0
            
                for num in self.oppSBRaiseMatrix[raiseRound]:
                    if num > raiseRatio:
                        numLarger += 1
                    elif num < raiseRatio:
                        numSmaller += 1
                        
                if raiseRound == 0:
                    lowPercent = int(100 * float(numLarger) / len(self.oppSBRaiseMatrix[raiseRound]))
                    highPercent = int(100 * (1 - float(numSmaller) / len(self.oppSBRaiseMatrix[raiseRound])))
                elif raiseRound == 1:
                    lowPercent = int(100 * (float(self.oppSBFirstRaiseTimes) / self.oppSBFirstTotalTimes) * (float(numLarger) / len(self.oppSBRaiseMatrix[raiseRound])))
                    highPercent = int(100 * (float(self.oppSBFirstRaiseTimes) / self.oppSBFirstTotalTimes) * (1 - float(numSmaller) / len(self.oppSBRaiseMatrix[raiseRound])))
              
                if highPercent - lowPercent < 10:
                    highPercent = min(100, highPercent + (1 + 10 - (highPercent - lowPercent)) / 2)
                    lowPercent = max(0, lowPercent - (10 - (highPercent - lowPercent)) / 2)
                    
                self.oppRange = [float(lowPercent) / 100, float(highPercent) / 100]
                            