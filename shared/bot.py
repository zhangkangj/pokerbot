'''
Created on Jan 8, 2013

@author: zhk
'''

class Bot(object): 
    def initialize(self):
        self.name = None
        self.oppName = None
        self.stackSize = None
        self.bb = None
        self.myBank = []
        
        self.button = None
        self.holeCards = []
        self.handID = None
        
        self.numBoardCards = None
        self.boardCards = []
        self.potSize = None
        
        self.time = None
        self.recentActions = []
        self.lastActions = None
        self.myLastAction = None
        self.oppLastAction = None
        self.actions = []
        self.minBet = None
        self.maxBet = None
        self.canRaise = None
        self.canCheck = None
    
    def __init__(self, socket):                
        self.socket = socket
        self.initialize()
        
    # private methods
    def run(self, input_socket):
        f_in = input_socket.makefile()
        while True:
            data = f_in.readline().strip()
            if not data:
                print "Gameover, engine disconnected."
                break

            print data
            parts = data.split()
            word = parts[0]
            
            if word == "NEWGAME":
                self.name = parts[1]
                self.oppName = parts[2]
                self.stackSize = int(parts[3])
                self.bb = int(parts[4])
            elif word == "NEWHAND":
                self.handID = int(parts[1])
                if parts[2] == "false":
                    self.button = False
                else:
                    self.button = True
                self.position = self.button
                self.holeCards = [parts[3], parts[4], parts[5]]
                self.myBank.append(int(parts[6]))
                self.time = float(parts[8])
                self.numBoardCards = 0
                self.recentActions = []
                self.oppLastAction = None
            elif word == "HANDOVER": #if opp folds and we haven't checked the board, could read the board here
                pass
            elif word == "KEYVALUE": #can ignore unless we are storing opp's info between games
                pass
            elif word == "REQUESTKEYVALUES":
                self.socket.send("FINISH\n")
            elif word == "GETACTION":
                self.potSize = int(parts[1])
                self.numBoardCards = int(parts[2])
                numLastActions = int(parts[3+self.numBoardCards])
                # better parser
                self.lastActions = parts[4+self.numBoardCards:(4+self.numBoardCards)+numLastActions]
                for action in self.lastActions:
                    if action.endswith(self.oppName):
                        self.oppLastAction = action[0:(len(action)-len(self.oppName)-1)]
                offset = 4 + self.numBoardCards + numLastActions
                numLegalActions = int(parts[offset])
                #better parser
                self.actions = parts[1+offset:1+offset+numLegalActions]
                for action in self.actions:
                    if action.startswith("RAISE") or action.startswith("BET"):
                        temp = action.split(":")
                        self.minBet = int(temp[1])
                        self.maxBet = int(temp[2])
                self.time = float(parts[1+offset+numLegalActions]) 
                
                if self.numBoardCards == 0: #preflop
                    self.preflop()
                elif self.numBoardCards == 3: #flop
                    if "DISCARD" in self.actions:
                        self.discard()
                    else:
                        self.flop()
                elif self.numBoardCards == 4: #turn                    
                    self.turn()
                else: #river                    
                    self.river()
            
        # Clean up the socket.
        self.socket.close()
   
    # public methods
    def preflop(self):
        self.check()
    
    def flop(self):
        self.check()
    
    def turn(self):
        self.check()
    
    def river(self):
        self.check()
    
    def showdown(self):
        pass
    
    #actions
    def check(self):
        #print "checking"
        self.myLastAction = "CHECK"
        self.socket.send("CHECK\n")
        
    def call(self):
        #print "calling"
        self.myLastAction = "CALL"
        self.socket.send("CALL\n")
    
    def rais(self, amount):
        amount = max(min(amount, self.maxBet), self.minBet)
        if self.canRaise == None:
            self.call()
            print "Raise Exception" 
        elif self.canRaise:
            #print "raising:"+str(amount)
            self.myLastAction = "RAISE:" + str(amount)
            self.socket.send("RAISE:" + str(amount) + "\n")
        else:
            print "Raise Exception"
            self.bet(amount)
    
    def bet(self, amount):
        #print "betting:"+str(amount)
        self.myLastAction = "BET:" + str(amount)
        self.socket.send("BET:" + str(amount) + "\n")
    
    def fold(self):
        if self.canCheck:
            self.check()
        else:
            #print "folding"
            self.myLastAction = "FOLD"
            self.socket.send("FOLD\n")
        
    def discard(self, card):
        #print "discarding"
        self.myLastAction = "DISCARD"
        self.socket.send("DISCARD:" + card + "\n")