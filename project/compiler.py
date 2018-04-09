# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml, copy
from base import *
from machine import *
from actions import *
from bartok import *
import colors
load = Machine.payload
debugmode = True
def log(msg):
    if debugmode:
        print(colors.magenta(str(msg)))

def precompile(script):
    script = json.dumps(yaml.load(script), sort_keys=True, indent=2)
    script = str(script).lower()
    script = re.sub(r'\bnull\b', '[]', script)
    # log(script)
    script = json.loads(script)
    script = convert(script)
    # print(type(script.decks[0]))
    for deck in script.decks:
        if not isinstance(deck.contents, list):
            deck.contents = deck.contents.split(' ')
    return script

def compile(script):
    initload(script)
    specStr = buildspec(script)
    exec(specStr, globals())
    log(spec)
    # return o(run=lambda:print('asdf'))
    return make(Machine("CUSTOM_GAME"), spec_bartok)

# ###########################################################
# deck: ['3d', '1s', '5d', '8c', '9h', '9c', '7s', '3c', '2c', '13c', '12s', '6s', '10s', '11h', '3s', '6c', '10d', '4s', '13s', '11c', '7c', '11d', '9s', '4h', '8h', '4c', '7d', '5s', '1d', '11s', '2d', '1h']
# pile: []
# hands:
	# player1: ['10h', '13h', '13d', '12h', '3h']
	# player2: ['12c', '9d', '8s', '6d', '12d']
	# player3: ['5h', '2h', '5c', '1c', '6h']
	# player4: ['10c', '4d', '8d', '2s', '7h']
# current player: 1
# starting player: 1
# scores: [0, 0, 0, 0]
# ###########################################################

def initload(script):pass
    # if 'decks' in script.__dict__:
    #     for deck in script.decks:
    #         load[deck.name] = deck.contents
    # if 'players' in script.__dict__:
    #     for player in script.players:
    #         load[player] = deck.contents
    #         if 'player attributes' in script.__dict__:
    #             load[player] = copy.deepcopy(script['player attributes'])
    # if 'game attributes' in script.__dict__:
    #         for key,val in script['game attributes'].items():
    #             load[key] = val

def buildspec(script):
    return """def spec(m, s, t):
        start      = s("start|>")
        gamestart  = s("new game is starting")
        turnstart  = s("new turn is starting")
        roundstart = s("new round is starting")
        end        = s("end game.")

        def chooseAndPlay():
            log(load)
            chooseCard()
            while not playIsValid():
                invalidMessage()
                chooseCard()
            play()

        turnstart.onEntry = chooseAndPlay

        t(start      , [m.true]     , [initPayload                         , initGame], gamestart            )  # prepare game data and setup for new game
        t(gamestart  , [m.true]     , []                                   , turnstart                       )  # player starts turn by choosing a card from hand or drawing one
        t(turnstart  , [handIsEmpty], [incrementScore, announceGameWinner] , roundstart                      )  # if player hand is empty then anounce game winner and give player 1 point
        t(turnstart  , [m.true]     , [rotatePlayer]                       , turnstart                       )  # if player hand is not empty then rotate player and have new player start turn by choosing a card from hand or drawing one 
        t(roundstart , [hasFive]    , [announceGameSetWinner]              , end                             )  # if player reaches 5 points then they win the gameset and gameset ends
        t(roundstart , [m.true]     , [rotateStartingPlayer                , initGame], gamestart            )  # if player has less than 5 points then rotate starting player and setup new game
"""

def run():
    script = """
    DECKS:
        -   name : face deck 
            contents : 1h 2h 3h 4h 5h 6h 7h 8h 9h 10h 11h 12h 13h 1s 2s 3s 4s 5s 6s 7s 8s 9s 10s 11s 12s 13s 1d 2d 3d 4d 5d 6d 7d 8d 9d 10d 11d 12d 13d 1c 2c 3c 4c 5c 6c 7c 8c 9c 10c 11c 12c 13c
            shuffle : yes
            hidden: yes
        -   name : draw deck
            contents :
            shuffle : no
            hidden : no
    PLAYERS:
        - player1
        - player2
        - player3
        - player4
    PLAYER ATTRIBUTES:
        score : 0
        hand :
    GAME ATTRIBUTES:
        current player : 1
        starting player: 1
    """

    script = precompile(script)
    compile(script).run()