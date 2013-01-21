'''
Created on Jan 21, 2013

@author: jhwan

'''

class Statistician:
    def __init__(self):
        pass
    
    def ProcessOppRaiseStats(self, dealer, raiseRound, oppAction, raiseRatio = 0):
        if dealer:
            if raiseRound == 1:
                self.oppBBFirstTotalTimes += 1
            
            if oppAction == "FOLD":                                   
                raiseRatio = -1
            elif oppAction == "CALL":
                raiseRatio = 0
            elif oppAction == "RAISE" and raiseRound == 1:             
                self.oppBBFirstRaiseTimes += 1
            
            # if we don't have enough cases
            if len(self.oppBBRaiseMatrix[raiseRound]) < 30:
                if raiseRound == 1:
                    if oppAction == "FOLD":
                        self.oppRange = [0.5,1]
                    elif oppAction == "CALL":
                        self.oppRange = [0.2,0.5]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.2]
                        
                if raiseRound == 2:
                    if oppAction =="FOLD":
                        self.oppRange = [0.1,0.2]
                    elif oppAction == "CALL":
                        self.oppRange = [0.05,0.1]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.05]
            else:
                numLarger = 0
                numSmaller = 0
            
                for num in self.oppBBRaiseMatrix[raiseRound]:
                    if num > raiseRatio:
                        numLarger += 1
                    elif num < raiseRatio:
                        numSmaller += 1
                        
                if raiseRound == 1:
                    lowPercent = int(100 * float(numLarger) / len(self.oppBBRaiseMatrix[raiseRound]))
                    highPercent = int(100 * (1 - float(numSmaller) / len(self.oppBBRaiseMatrix[raiseRound])))
                elif raiseRound == 2:
                    lowPercent = int(100 * (float(self.oppBBFirstRaiseTimes) / self.oppBBFirstTotalTimes) * (float(numLarger) / len(self.oppBBRaiseMatrix[raiseRound])))
                    highPercent = int(100 * (float(self.oppBBFirstRaiseTimes) / self.oppBBFirstTotalTimes) * (1 - float(numSmaller) / len(self.oppBBRaiseMatrix[raiseRound])))
              
                if highPercent - lowPercent < 10:
                    highPercent = min(100, highPercent + (1 + 10 - (highPercent - lowPercent)) / 2)
                    lowPercent = max(0, lowPercent - (10 - (highPercent - lowPercent)) / 2)
                    
                self.oppRange = [float(lowPercent) / 100, float(highPercent) / 100]
                        
            self.oppBBRaiseMatrix[raiseRound].append(raiseRatio)

            if len(self.oppBBRaiseMatrix[raiseRound]) > 100:
                self.oppBBRaiseMatrix[raiseRound].pop(0)
        else:  
            if raiseRound == 1:
                self.oppSBFirstTotalTimes += 1
            
            if oppAction == "FOLD":                                   
                raiseRatio = -1
            elif oppAction == "CALL":
                raiseRatio = 0
            elif oppAction == "RAISE" and raiseRound == 1:             
                self.oppSBFirstRaiseTimes += 1
                
            if len(self.oppSBRaiseMatrix[raiseRound]) < 30:
                if raiseRound == 1:
                    if oppAction == "FOLD":
                        self.oppRange = [0.9,1]
                    elif oppAction == "CALL":
                        self.oppRange = [0.6,0.9]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.6]
                        
                if raiseRound == 2:
                    if oppAction =="FOLD":
                        self.oppRange = [0.5,0.6]
                    elif oppAction == "CALL":
                        self.oppRange = [0.1,0.5]
                    elif oppAction == "RAISE":
                        self.oppRange = [0,0.1]
            else:
                numLarger = 0
                numSmaller = 0
            
                for num in self.oppSBRaiseMatrix[raiseRound]:
                    if num > raiseRatio:
                        numLarger += 1
                    elif num < raiseRatio:
                        numSmaller += 1
                        
                if raiseRound == 1:
                    lowPercent = int(100 * float(numLarger) / len(self.oppSBRaiseMatrix[raiseRound]))
                    highPercent = int(100 * (1 - float(numSmaller) / len(self.oppSBRaiseMatrix[raiseRound])))
                elif raiseRound == 2:
                    lowPercent = int(100 * (float(self.oppSBFirstRaiseTimes) / self.oppSBFirstTotalTimes) * (float(numLarger) / len(self.oppSBRaiseMatrix[raiseRound])))
                    highPercent = int(100 * (float(self.oppSBFirstRaiseTimes) / self.oppSBFirstTotalTimes) * (1 - float(numSmaller) / len(self.oppSBRaiseMatrix[raiseRound])))
              
                if highPercent - lowPercent < 10:
                    highPercent = min(100, highPercent + (1 + 10 - (highPercent - lowPercent)) / 2)
                    lowPercent = max(0, lowPercent - (10 - (highPercent - lowPercent)) / 2)
                    
                self.oppRange = [float(lowPercent) / 100, float(highPercent) / 100]
                        
            self.oppSBRaiseMatrix[raiseRound].append(raiseRatio)

            if len(self.oppSBRaiseMatrix[raiseRound]) > 100:
                self.oppSBRaiseMatrix[raiseRound].pop(0)                
    