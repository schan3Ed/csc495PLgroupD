# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml
from base import *
from machine import *
from actions import *
import bartok
import colors

debugmode=True
def log(msg):
    if debugmode:
        print(colors.magenta(str(msg)))

def precompile(script):
    script = json.dumps(yaml.load(script), sort_keys=True, indent=2)
    script = str(script).lower()
    log(script)
    script = json.loads(script)
    script = convert(script)
    print(type(script.decks[0]))
    for deck in script.decks:
        deck.contents = deck.contents.split(' ') if deck.contents!=None else []
    log(script)
    return script

def compile(script):
    return make(Machine("CUSTOM_GAME"),
        lambda m,t,s: bartok.spec_bartok(m,t,s)
    )




script = """
DECKS:
    -   name : face deck 
        contents : 1h 2h 3h 4h 5h 6h 7h 8h 9h 10h 11h 12h 13h 1s 2s 3s 4s 5s 6s 7s 8s 9s 10s 11s 12s 13s 1d 2d 3d 4d 5d 6d 7d 8d 9d 10d 11d 12d 13d 1c 2c 3c 4c 5c 6c 7c 8c 9c 10c 11c 12c 13c
        shuffle : yes
        hidden: yes
    -   name : draw deck
        contents :
        shuffle : no
        hidden: no
PLAYERS :
    - player1
    - player2
    - player3
    - player4
"""

script = precompile(script)
compile(script).run()
##############################
########### RUNNER ###########
##############################
def run():
    """wrapped try catch here so that it doesn't catch sub machines, only parent machine"""
    try:
        make(Machine("CUSTOM_GAME"), compile).run()
    except State.FSMLimit as e:
        print(e.args[0].upper())
##############################


##############################
############ SPEC ############
##############################
def spec_bartok(m, s, t):
    start     = s("start|>"             )
    newgame   = s("game starts"         )
    startturn = s("player turn has started" )          
    endturn   = s("player turn has ended"   )
    wingame   = s("player wins"         )
    endgame   = s("end game."           )

    def logBeforeTurn():
        print(colors.magenta("\n# AFTER PLAYER'S CHOICE BUT BEFORE CARD IS PLAYED"))
        log(None)
    def logAfterTurn():
        print(colors.magenta("\n# AFTER CARD IS PLAYED"))
        log(None)
    startturn.onEntry = logBeforeTurn
    endturn.onEntry = logAfterTurn

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

  # t(FROM      , GAURDS        , ACTIONS                              , TO)
    t(start     , [m.true]      , [initPayload ,initGame]              , newgame   ) # prepare game data and setup for new game
    t(newgame   , [m.true]      , [chooseCard]                         , startturn ) # player starts turn by choosing a card from hand or drawing one
    t(startturn , [playIsValid] , [play]                               , endturn   ) # if chosen card is valid choice based on game rules then play the card
    t(startturn , [m.true]      , [invalidMessage, chooseCard]         , startturn ) # if chosen card isn't valid then display error and choose again
    t(endturn   , [handIsEmpty] , [incrementScore, announceGameWinner] , wingame   ) # if player hand is empty then anounce game winner and give player 1 point
    t(endturn   , [m.true]      , [rotatePlayer, chooseCard]           , startturn ) # if player hand is not empty then rotate player and have new player start turn by choosing a card from hand or drawing one 
    t(wingame   , [hasFive]     , [announceGameSetWinner]              , endgame   ) # if player reaches 5 points then they win the gameset and gameset ends
    t(wingame   , [m.true]      , [rotateStartingPlayer, initGame]     , newgame   ) # if player has less than 5 points then rotate starting player and setup new game
##############################