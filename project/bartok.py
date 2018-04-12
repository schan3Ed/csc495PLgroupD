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
        make(Machine("BARTOK"), spec_bartok).run()
    except State.FSMLimit as e:
        print(e.args[0].upper())
##############################


##############################
############ SPEC ############
##############################
def spec_bartok(m, s, t):
    start     = s("start|>"             )
    gamestart   = s("new game is started"         )
    turnstart = s("new turn is started" )           
    roundstart   = s("new round is started"         )
    end   = s("end game."           )

    def chooseAndPlay():
        print(colors.magenta(str(load)))
        chooseCard()
        while not playIsValid():
            invalidMessage()
            chooseCard()
        play()
    turnstart.onEntry = chooseAndPlay
    





    # all guards must be true before actions are executed and machine procedes to next state
    # all guards, actions, and transitions(for a given start state) are executed in order of appearance
    # this means the following 2 exampes are identical
    # EXAMPLE 1
    # t(s1, [g1], [a1], s2)
    # t(s1, [m.true], [a1], s2)
    # EXAMPLE 2
    # t(s1, [g1], [a1], s2)
    # t(s1, [lambda t: not g1(t)], [a1], s2)
    # this is because the second transition's guards are only called if at least one of the previous transition's guards returned False 

  # t(FROM       , GAURDS        , ACTIONS                              , TO)
    t(start      , [m.true]      , [initPayload ,initGame]              , gamestart    ) # prepare game data and setup for new game
    t(gamestart  , [m.true]      , []                                   , turnstart    ) # player starts turn by choosing a card from hand or drawing one
    t(turnstart  , [handIsEmpty] , [incrementScore, announceGameWinner] , roundstart   ) # if player hand is empty then anounce game winner and give player 1 point
    t(turnstart  , [m.true]      , [rotatePlayer]                       , turnstart    ) # if player hand is not empty then rotate player and have new player start turn by choosing a card from hand or drawing one 
    t(roundstart , [hasFive]     , [announceGameSetWinner]              , end          ) # if player reaches 5 points then they win the gameset and gameset ends
    t(roundstart , [m.true]      , [rotateStartingPlayer, initGame]     , gamestart    ) # if player has less than 5 points then rotate starting player and setup new game
##############################


##############################
### ACTIONS/GUARDS/HELPERS ###
##############################
def initGame():
    load.currentPlayer=load.startingPlayer
    initDecks()
    deal()

def chooseCard():
    options = hand() + ['draw']
    return choose("Player%s, play a card"%load.currentPlayer,options, autoplay=False) == 'draw'

def initPayload():
    load["startingPlayer"]=1
    load["currentPlayer"]=1
    load["numPlayers"]=4
    load["initialHandSize"]=5
    load.scores = [0 for i in range(0, load.numPlayers)]
    drawDeck = shuffle([str(rank) + suit for suit in ['h','s','d','c'] for rank in range(1,14)])
    faceDeck = []
    load["initialDecks"] = [drawDeck, faceDeck]
    initDecks()

def playIsValid():
    # return True
    if len(load.decks[1]) == 0:
        return True
    choice = load.choice
    if choice == 'draw':
        return True
    topCard = load.decks[1][-1]
    if isSameSuit(choice, topCard) or isSameRank(choice, topCard):
        return True
    return False

def incrementScore():
    load.scores[load.currentPlayer-1]+=1

def announceGameWinner():
    print(colors.negative("\nPLAYER %s wins this game" % load.currentPlayer))
    scores = ["player%s: %s" % (idx+1,score) for idx, score in enumerate(load.scores)]
    print(colors.negative("Gameset Scoreboard:\n%s\n" % indentedlist(scores, indent=1)))

# def log(i):
#     def printlog(s): print(colors.magenta(s))
#     printlog("# ###########################################################")
#     printlog("# deck: %s" % load.decks[0])
#     printlog("# pile: %s" % load.decks[1])
#     hands = ["# player%s: %s" % (idx+1,hand) for idx, hand in enumerate(load.playerHands)]
#     printlog("# hands: \n%s" % indentedlist(hands, indent=1))
#     if 'choice' in load.keys():
#         printlog("# choice: %s" % load.choice)
#     printlog("# current player: %s" % load.currentPlayer)
#     printlog("# starting player: %s" % load.startingPlayer)
#     printlog("# scores: %s" % load.scores)
#     # printlog("state path: " + load.path)
#     printlog("# ###########################################################\n")
#############################