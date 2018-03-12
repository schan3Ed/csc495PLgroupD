from base import *
from machine import *
# ---------------------------------------
from actions import *

def spec_bartok(m, s, t):
    start     = s("start|>"             )
    newgame   = s("game starts"         )
    startturn = s("player turn started" )           
    endturn   = s("player turn ended"   )
    wingame   = s("player wins"         )
    endgame   = s("end game."           )
    # startturn.onEntry = log

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

  # t(FROM      , GAURDS        , ACTIONS                            , TO)
    t(start     , [m.true]      , [initPayload ,initGame, log]       , newgame   ) 
    t(newgame   , [m.true]      , [selectCardOrDraw]                 , startturn )
    t(startturn , [playIsValid] , [playCardOrDraw, log]              , endturn   ) # checks validity, if valid, performs the player's choice
    t(startturn , [m.true]      , [invalidMessage, selectCardOrDraw] , startturn )

    t(endturn   , [handIsEmpty] , [incrementScore, announceWinner]   , wingame   ) # play hand is empty
    t(endturn   , [m.true]      , [rotatePlayer, selectCardOrDraw]   , startturn ) # player hand not empty 
    t(wingame   , [hasFive]     , None                               , endgame   ) # player has 5 points 
    t(wingame   , [m.true]      , [rotateStartingPlayer, initGame]   , newgame   ) # player has less 5 points


def spec_spade(m, s, t):
    start     = s("start|>"             )
    newgame   = s("game starts"         )
    startturn = s("player turn started" )           
    endturn   = s("player turn ended"   )
    endRound  = s("player round ended"  )
    wingame   = s("player wins"         )

    t(start,        [m.true],               [initPayloadSpades, initGameSpade, log], newgame     )
    t(newgame,      [m.true],               [selectCardOrDraw],                      startturn   )
    t(startturn,    [m.true],               [playCardOrDraw, log],                   endturn     )
    t(endturn,      [notEqualHands],        [rotatePlayer, selectCardOrDraw],        startturn   )
    t(endturn,      [m.true],               [updatePoints,],                         endRound    )
    t(endRound,     [handIsEmpty, hasFive], [announceWinner],                        wingame     )
    t(endRound,     [handIsEmpty],          [initPayloadSpades],                     newgame     )
    t(endRound,     [m.true],               [cleanPile, selectCardOrDraw],           startturn   )
    return

# @ok
def machine2():
    """preserved original machine 2"""
    make(MyMachine("playtime"), spec001).run()

@ok
def machine3():
    """wrapped try catch here so that it doesn't catch sub machines, only parent machine"""
    try:
        make(Machine("bartok"), spec_spade).run()
        print('\nFINAL PAYLOAD = ' + str(load))
    except State.FSMLimit as e:
        print(e.args[0].upper())
