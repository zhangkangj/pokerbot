'''
Created on Jan 21, 2013

@author: zhk
'''
import matplotlib.pyplot as plt

if __name__ == '__main__':
    f = open("match/day7/Casino_Day-7_RAISE_vs_Yipee.txt")
    total = winAmount = lossAmount = 0 
    win = loss = 0
    cache = []
    amounts = []
    bank = []
    isDealer = True
    for line in f.readlines():
        line = line.strip()
        cache.append(line)
        if "wins" in line:
            begin = line.index("(")
            end = line.index(")")
            amount = int(line[begin+1:end])
            if not line.startswith("RAISE"):
                amount = - amount
            amounts.append(amount)
        if "Hand #" in line:
            parts = line.split(",")
            if "RAISE" in parts[1]:
                string = parts[1]
            else:
                string = parts[2]
            begin = string.index("(")
            end = string.index(")")
            amount = int(string[begin+1:end])
            bank.append(amount)
        if line.strip() == "":
            if abs(amount) >= 0 and abs(amount) < 100:
                total += amount
                if amount > 0:
                    winAmount += amount
                    win += 1
                else:
                    lossAmount += amount
                    loss +=1
                for message in cache:
                    print message
            cache = []    
    print total, winAmount, lossAmount
    print win + loss, win, loss, 1.0 * win/ (win+loss)
    print total / (win+loss)
    plt.subplot(210)
    plt.plot(bank)
    plt.subplot(211)
    plt.plot(amounts)
    plt.show()