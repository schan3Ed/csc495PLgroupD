# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
from base  import *
from machine import *
from actions import *


##############################
########### RUNNER ###########
##############################
def run():
    """wrapped try catch here so that it doesn't catch sub machines, only parent machine"""
    try:
        make(Machine("SPADES"), spec_spades).run()
    except State.FSMLimit as e:
        print(e.args[0].upper())
    print(load.path)
#############################


##############################
############ SPEC ############
##############################
def spec_spades(m, s, t):
    start     = s("start|>")
    gamestart = s("game started")
    startturn = s("turn started")
    endturn   = s("turn ended")
    roundwon  = s("round won")
    end       = s("end.")
    def logBeforeTurn():
        print(colors.magenta("\nAFTER PLAYER'S CHOICE BUT BEFORE CARD IS PLAYED"))
        log(None)
    def logAfterTurn():
        print(colors.magenta("\nAFTER CARD IS PLAYED"))
        log(None)
    startturn.onEntry = logBeforeTurn
    endturn.onEntry = logAfterTurn

    t(start     , [m.true]                           , [initPayload, initGame, initRound]             , gamestart ) # prepare game data and setup new game
    t(gamestart , [m.true]                           , [chooseCard]                                   , startturn ) # player starts turn by choosing a card from hand
    t(startturn , [playIsValid]                      , [play]                                         , endturn   ) # if chosen card is valid choice based on game rules, then play card
    t(startturn , [m.true]                           , [invalidMessage,chooseCard]                    , endturn   ) # if chosen card isn't valid, then display error and choose again
    t(endturn   , [equalHands]                       , [grantPoint]                                   , roundwon  ) # if all players have played one card then calculate round winner and update game points
    t(endturn   , [m.true]                           , [rotatePlayer, chooseCard]                     , startturn ) # if not all players have played one card then rotate player and have new player start turn by choosing a card from hand
    t(roundwon  , [allHandsEmpty, aboutToWinGameSet] , None                                           , end       ) # if all player hands are empty and game winner is about to win gameset then gameset ends
    t(roundwon  , [allHandsEmpty]                    , [incrementScore, announceGameWinner, initGame] , gamestart ) # if all player hands are empty and game winner isn't about to win gameset then update score and setup new game
    t(roundwon  , [m.true]                           , [initRound, chooseCard]                        , startturn ) # if not all player hands are empty then rotate round starting player and start new round by having the player choose card from hand
##############################


##############################
### ACTIONS/GUARDS/HELPERS ###
##############################
def initRound(t):
    load["roundStartingPlayer"] = ((load.startingPlayer-1+(load.initialHandSize-len(hand()))) % load.numPlayers) + 1
    load.currentPlayer = load.roundStartingPlayer
    
def initGame(t):
    load.points = [0 for i in range(0, load.numPlayers)]
    initDecks()
    deal()

def initPayload(t):
    load["startingPlayer"]=1
    load["currentPlayer"]=1
    load["numPlayers"]=4
    load["initialHandSize"]=13
    load.points = [0 for i in range(0, load.numPlayers)]
    load.scores = [0 for i in range(0, load.numPlayers)]
    drawDeck = shuffle([str(rank) + suit for suit in ['h','s','d','c'] for rank in range(1,14)])
    faceDeck = []
    load["initialDecks"] = [drawDeck, faceDeck]
    initDecks()

def chooseCard(t):
    options = hand()
    return choose("Player%s, play a card"%load.currentPlayer,options,autoplay=False) == 'draw'

def grantPoint(t):
    roundwinner = roundWinner()
    load.points[roundwinner-1]+=1
    print("\n" + colors.negative("Player %s wins round." % (roundwinner)))
    points = ["player%s: %s" % (idx+1,score) for idx, score in enumerate(load.points)]
    print(colors.negative("Game Points Scoreboard:\n%s\n" % indentedlist(points, indent=1)))

def roundWinner():
    roundCards = load.decks[1][-4:]
    roundTotals = [cardValue(idx,card, roundCards) for idx,card in enumerate(roundCards)]
    return (roundTotals.index(max(roundTotals))+load.roundStartingPlayer-1) % load.numPlayers + 1

def cardValue(idx, card, roundCards):
    val=0
    isSpade = bool(card[-1]=='s')
    if idx!=0:
        previous = roundCards[idx-1]
        first = roundCards[0]
        if not isSameSuit(card, first) and not isSpade:
            return 0;
    if isSpade: val+=13
    val+=int(card[:-1])
    return val

def gameWinner():
    return load.points.index(max(load.points))+1

def playIsValid(t): # TODO no checks for validity. Any card is playable atm.
    return True

def aboutToWinGameSet(t):
    return load.scores[gameWinner()-1] == 4

def incrementScore(t):
    load.scores[gameWinner()-1]+=1

def log(i):
    def printlog(s): print(colors.magenta(s))
    printlog("###########################################################")
    printlog("deck: %s" % load.decks[0])
    printlog("pile: %s" % load.decks[1])
    numberOfRoundCards = load.numPlayers-(len(load.decks[1])%load.numPlayers)
    printlog("round cards: %s" % load.decks[1][-1*numberOfRoundCards:])
    printlog("round starting player: %s" % load.roundStartingPlayer)
    hands = ["player%s: %s" % (idx+1,hand) for idx, hand in enumerate(load.playerHands)]
    printlog("hands: \n%s" % indentedlist(hands, indent=1))
    if 'choice' in load.keys():
        printlog("choice: %s" % load.choice)
    printlog("current player: %s" % load.currentPlayer)
    printlog("starting player: %s" % load.startingPlayer)
    printlog("scores: %s" % load.scores)
    printlog("state path: " + load.path)
    printlog("###########################################################\n")

def announceGameWinner(t):
    print(colors.negative("\nPLAYER %s wins this game" % gameWinner()))
    scores = ["player%s: %s" % (idx+1,score) for idx, score in enumerate(load.scores)]
    print(colors.negative("Gameset Scoreboard:\n%s\n" % indentedlist(scores, indent=1)))
##############################