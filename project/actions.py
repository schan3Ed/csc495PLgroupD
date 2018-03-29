# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
from base  import *
from machine import *

load = Machine.payload

def initDecks():
    # clone from initial deck state
    load["decks"] = [shuffle([card for card in deck]) for deck in load["initialDecks"]]

def transferCards():
    load.decks[0] = shuffle(load.decks[1][:-1])
    load.decks[1]=[load.decks[1][-1]]

def deal():
    load["playerHands"]=[[] for i in range(4)]
    for p in load.playerHands:
        for i in range(0,load.initialHandSize):
            draw(p)

def draw(hand):
    if len(load.decks[0]) == 0:
        transferCards()
    hand+=[load.decks[0][0]]
    load.decks[0].remove(hand[-1])

def choose(prompt, options, autoplay=None):
    autoplay = autoplay or False
    if autoplay:
        choice = random.choice(options)
        # BELOW WILL MIMIC PLAYER INTERATION WHILE AUTOPLAYING. USEFUL FOR GENERATING SCRIPTS FOR HW SUBMISSION.
        # choice = options[0] # random.choice(options)
        # print("%s (type a number then hit Enter)" % prompt)
        # print("\n".join(["%i: %s" % (idx,option) for idx, option in enumerate(options)]))
        # print("enter a number: 0")
        # print(colors.negative("YOU CHOSE %s" % choice))
    else:
        choice = None
        while choice is None:
            try:
                print("%s (type a number then hit Enter)" % prompt)
                print("\n".join(["%i: %s" % (idx,option) for idx, option in enumerate(options)]))
                number = int(input("enter a number: "))
                if number < 0 or number >= len(options):
                    raise IndexError("INVALID INPUT: that number is not an option")
                choice = options[number]
                print(colors.negative("YOU CHOSE %s" % choice))
            except Exception as e:
                invalidMessage(None)
    load["choice"]=choice
    return choice

def rotateStartingPlayer(t):
    load.startingPlayer=load.startingPlayer%load.numPlayers+1

def rotatePlayer(t):
    load.currentPlayer=load.currentPlayer%load.numPlayers+1

def play(t):
    card = load.choice
    if card == 'draw':
        draw(hand())
    if card in hand():
        load.decks[1]+=[card]
        hand().remove(card)

def handIsEmpty(t):
    return len(hand()) == 0

def allHandsEmpty(t):
    for hand in load.playerHands:
        if len(hand)!=0: return False
    return True

def hand():
    return load.playerHands[load.currentPlayer-1]

def equalHands(t):
    l = len(hand())
    for h in load.playerHands:
        if len(h) != l:
            return False
    return True

def hasFive(t):
    return load.scores[load.currentPlayer-1]==5

def isSameSuit(c1, c2):
    return bool(c1[-1]==c2[-1])

def isSameRank(c1, c2):
    return bool(c1[:-1]==c2[:-1])

def invalidMessage(t):
    print(colors.red("YOUR CHOICE IS INVALID"))

    
def announceGameSetWinner(t):
    print(colors.negative("!!! GAMESET WINNER IS Player %s !!!" % str(load.scores.index(max(load.scores))+1)))