from base import *
from machine import *
# ---------------------------------------
def spec002(m, s, t):
    start = s("start|>")
    first = s("substate1")
    t(start, m.true, None, first)
    t(first, m.maybe,  None, "end.")
    t(first, m.maybe,  None, first)

def spec003(m, s, t):
    def sampleAction(currentTransition):
        Machine.payload.path+="@#$% "
    start = s("start|>")
    first = s("state1")
    second = s("state2")
    second._submachine = make(SubMachine("more playtime", m), spec002)
    third = s("state3")
    t("start|>", m.true, None, first)
    t(first, m.true, sampleAction, second)
    t(second, m.maybe, None, third)
    t(second, m.maybe, None, first)
    t(third, m.true, None, "end.")

def spec_bartok(m, s, t):
    start =     s("start|>"             )
    newgame =   s("game starts"         )
    startturn = s("player turn started" )
    endturn =   s("player turn ended"   )
    wingame =   s("player wins"         )
    endgame =   s("end game."            )
    t(start     , m.true     , None, newgame   )                                
    t(newgame   , m.true     , None, startturn )                                
    t(startturn , m.likely   , None, endturn   ) # player has playable card 
    t(startturn , m.true     , None, endturn   )                                
    t(endturn   , m.likely   , None, startturn ) # player hand not empty    
    t(endturn   , m.unlikely , None, wingame   ) # play hand is empty       
    t(wingame   , m.unlikely , None, endgame   ) # player has 5 points      
    t(wingame   , m.likely   , None, newgame   ) # player has less 5 points


# @ok
def machine2():
    """preserved original machine 2"""
    make(MyMachine("playtime"), spec001).run()

@ok
def machine3():
    """wrapped try catch here so that it doesn't catch sub machines, only parent machine"""
    try:
        make(Machine("bartok"), spec_bartok).run()
        print('\nFINAL PAYLOAD = ' + str(Machine.payload))
    except State.FSMLimit as e:
        print(e.args[0].upper())