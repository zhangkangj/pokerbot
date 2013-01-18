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
    
    def __init__(self, socket):                
        self.socket = socket
        self.initialize()
        
    # private methods
    def run(self, input_socket):
        f_in = input_socket.makefile()
        while True:
            message = f_in.readline().strip()
            if not message:
                print "Gameover, engine disconnected."
                break
            print message
            self.handleMessage(message)
        # Clean up the socket.
        self.socket.close()
    
    def handleMessage(self, message):
        parts = message.split()
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
            lastActionsString = parts[4+self.numBoardCards:(4+self.numBoardCards)+numLastActions] 
            self.lastActions = []
            for actionString in lastActionsString:
                temp = actionString.split(":")
                if len(temp) == 2:
                    self.lastActions.append((temp[0], temp[1]))
                    if temp[1] == self.oppName:
                        self.oppLastAction = (temp[0])
                else:
                    self.lastActions.append((temp[0], int(temp[1]), temp[2]))
                    if temp[2] == self.oppName:
                        self.oppLastAction = (temp[0], temp[1])

            offset = 4 + self.numBoardCards + numLastActions
            numLegalActions = int(parts[offset])
            actionsString = parts[1+offset:1+offset+numLegalActions]
            
            self.actions = []
            for actionString in actionsString:
                temp = actionString.split(":")
                self.actions.append(temp[0])
                if temp[0] == "RAISE" or temp[0] == "BET":
                    self.minBet = int(temp[1])
                    self.maxBet = int(temp[2])
            self.time = float(parts[2+offset+numLegalActions]) 
            
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
        self.myLastAction = ("CHECK")
        self.socket.send("CHECK\n")
        
    def call(self):
        #print "calling"
        self.myLastAction = ("CALL")
        self.socket.send("CALL\n")
    
    def rais(self, amount):
        amount = max(min(amount, self.maxBet), self.minBet)
        if self.canRaise == None:
            self.call()
            print "Raise Exception" 
        elif self.canRaise:
            #print "raising:"+str(amount)
            self.myLastAction = ("RAISE:", amount)
            self.socket.send("RAISE:" + str(amount) + "\n")
        else:
            print "Raise Exception"
            self.bet(amount)
    
    def bet(self, amount):
        #print "betting:"+str(amount)
        self.myLastAction = ("BET:", amount)
        self.socket.send("BET:" + str(amount) + "\n")
    
    def fold(self):
        if self.canCheck:
            self.check()
        else:
            #print "folding"
            self.myLastAction = ("FOLD")
            self.socket.send("FOLD\n")
        
    def discard(self, card):
        #print "discarding"
        self.socket.send("DISCARD:" + card + "\n")