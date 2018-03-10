# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random
from machine import *

load = Machine.payload

def initDecks():
    # clone from initial deck state
    load["decks"] = [[card for card in deck] for deck in load["initialDecks"]]

def transferCards(fromDeck, toDeck):
    toDeck = toDeck + fromDeck
    fromDeck = []

def deal():
    load["players"]=[[] for i in range(4)]
    d = load.decks[0]
    for p in load.players:
        for i in range(0,load.initialHandSize):
            draw(d,p)

def draw(deck, hand):
    if len(deck[0]) == 0:
        transferCards(deck[1],deck[0])
    hand+=[deck[0]]
    deck.remove(hand[-1])

def choose(prompt, options, autoplay=None):
    autoplay = autoplay or False
    if autoplay:
        choice = random.choice(options)
    else:
        print("%s (type a number then hit Enter)" % prompt)
        print("\n".join(["%i: %s" % (idx,option) for idx, option in enumerate(options)]))
        number = int(input("enter a number: "))
        choice = options[number]
        print("you chose %s" % choice)
    load["choice"]=choice
    return choice

def initPayload(t):
    load["startingPlayer"]=1
    load["currentPlayer"]=1
    load["numPlayers"]=4
    load["initialHandSize"]=5
    drawDeck = shuffle([str(rank) + suit for suit in ['h','s','d','c'] for rank in range(1,14)])
    faceDeck = []
    load["initialDecks"] = [drawDeck, faceDeck]
    initDecks()

def initPayloadSpades(t):
    load["startingPlayer"]=1
    load["currentPlayer"]=1
    load["numPlayers"]=4
    load["initialHandSize"]=13
    drawDeck = shuffle([str(rank) + suit for suit in ['h','s','d','c'] for rank in range(1,14)])
    faceDeck = []
    load["initialDecks"] = [drawDeck, faceDeck]
    load.points = [0 for i in range(0, load.numPlayers)]
    initDecks()
    deal()

def cleanPile(t):
    load.deck[1] = []
    
def initGame(t):
    load.currentPlayer=load.startingPlayer
    load.scores = [0 for i in range(0, load.numPlayers)]
    initDecks()
    deal()

def initGameSpade(t):
    load.currentPlayer=load.startingPlayer
    load.scores = [0 for i in range(0, load.numPlayers)]

def rotateStartingPlayer(t):
    load.startingPlayer=load.startingPlayer%load.numPlayers+1

def hand():
    return load.players[load.currentPlayer-1]

def rotatePlayer(t):
    load.currentPlayer=int(load.currentPlayer)%load.numPlayers+1

def selectCardOrDraw(t):
    options = hand() + ['draw']
    return choose("play a card",options,autoplay=False) == 'draw'

def chooseCard(t):
    return choose("play a card",options,autoplay=False) == 'draw'
    
    card = load.choice
    if card == 'draw':
        draw(load.decks[0], hand())
    if card in hand():
        load.decks[1]+=[card]
        hand().remove(card)

def playIsValid(t): # TODO no checks for validity. Any card is playable atm.
    return True

def handIsEmpty(t):
    return len(hand()) == 0

def announceWinner(t):
    print("\nPLAYER %s wins this game" % load.currentPlayer)
    scores = ["player%s: %s" % (idx,score) for idx, score in enumerate(load.players)]
    print("Updated Scoreboard:\n%s\n" % indentedlist(scores, indent=1))

def incrementScore(t):
    load.scores[load.currentPlayer-1]+=1

def hasFive(t):
    return load.scores[load.currentPlayer-1]==5

def invalidMessage(t):
    print("YOUR CHOICE IS INVALID")

def log(i):
    print("\ndeck: %s" % load.decks[0])
    print("pile: %s" % load.decks[1])
    hands = ["player%s: %s" % (idx,hand) for idx, hand in enumerate(load.players)]
    print("hands: \n%s" % indentedlist(hands, indent=1))
    if 'choice' in load.keys():
        print("choice: %s" % load.choice)
    print("current: %s\n" % load.currentPlayer)
