# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml, copy
from machine import *
# from actions import *
# from bartok import *
import colors
import helpers
import the

def yaml2json(text):
    text = json.dumps(yaml.load(the.script), sort_keys=True, indent=2)
    text = json.loads(text)
    return text

def precompile():
    # log(the.script)
    the.script = json.dumps(yaml.load(the.script), sort_keys=True, indent=2)
    the.script = str(the.script).lower()
    the.script = re.sub(r'\bnull\b', '[]', the.script)
    the.script = json.loads(the.script)
    the.script = o.convert(the.script)
    for deck in the.script.decks:
        if not isinstance(deck.contents, list):
            deck.contents = deck.contents.split(' ')
    return the.script

def compile():
    # log(the.script)
    initload()
    specStr = buildspec()
    exec(specStr, globals(), globals())
    return make(Machine("CUSTOM_GAME"), globals()['spec'])
    # return make(Machine("CUSTOM_GAME"), spec_bartok)
    
# OLD PAYLOAD STRUCTURE (log the.load during runtime to see new payload structure)
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

def initload():
    if 'decks' in the.script.__dict__:
        for deck in the.script.decks:
            the.load[deck.name] = deck.contents
    if 'players' in the.script.__dict__:
        for player in the.script.players:
            the.load[player] = deck.contents
            if 'player attributes' in the.script.__dict__:
                the.load[player] = copy.deepcopy(the.script['player attributes'])
    if 'game attributes' in the.script.__dict__:
            for key,val in the.script['game attributes'].items():
                the.load[key] = val

def buildspec():
    # log(the.script)
    name2instance = o.convert({
        "starting"             : "start",
        "new game is started"  : "gamestart",
        "new turn is started"  : "turnstart",
        "new round is started" : "roundstart",
        "game is finished"     : "end"
    })

    spec = """
def spec(m, s, t):"""
    
    for identifier, instanceName in name2instance.items():
        if instanceName=='start': identifier = "%s|>"%identifier
        if instanceName=='end'  : identifier = "%s." %identifier
        spec+="""
    %s = s("%s")""" % (instanceName, identifier)
    
    # TODO: remove expression bellow and allow the.script maker to specify card selection behavior
    spec+= """
    def chooseCard():
        options = the.load[the.load['current player']].hand + ['draw']
        return choose("%s, play a card"%the.load['current player'],options, autoplay=False) == 'draw'
    def playIsValid():
        if len(the.load['face deck']) == 0:
            return True
        choice = the.load.choice
        if choice == 'draw':
            return True
        topCard = the.load['face deck'][-1]
        if isSameSuit(choice, topCard) or isSameRank(choice, topCard):
            return True
        return False
    def draw(player):
        if len(the.load['draw deck']) is 0:
            transferCards()
        the.load[player].hand+=[the.load['draw deck'][0]]
        the.load['draw deck'].remove(the.load[player].hand[-1])
    def play():
        card = the.load.choice
        if card == 'draw':
            draw(the.load['current player'])
        elif card in the.load[the.load['current player']].hand:
            the.load['face deck']+=[card]
            the.load[the.load['current player']].hand.remove(card)
    def transferCards():
        the.load['draw deck'] = shuffle(the.load['face deck'][:-1])
        the.load['face deck']=[the.load['face deck'][-1]]
        
    def chooseAndPlay():
        # log(the.load)
        chooseCard()
        while not playIsValid():
            invalidMessage()
            chooseCard()
        play()
    turnstart.onEntry = chooseAndPlay
    """
    # spec+="""
    # t(start      , [m.true]      , [initPayload ,initGame]              , gamestart    )
    # t(gamestart  , [m.true]      , []                                   , turnstart    )
    # t(turnstart  , [handIsEmpty] , [incrementScore, announceGameWinner] , roundstart   )
    # t(turnstart  , [m.true]      , [rotatePlayer]                       , turnstart    )
    # t(roundstart , [hasFive]     , [announceGameSetWinner]              , end          )
    # t(roundstart , [m.true]      , [rotateStartingPlayer, initGame]     , gamestart    )"""
    the.script.rules = [re.sub("\"","\\\"",rule) for rule in the.script.rules]
    for rule in the.script.rules:
        transitionArgs = re.sub(r"\b(when|if|then|unless|so)\b", "-\\1:", rule).split('-')[1:]
        transitionArgs = [arg.split(':') for arg in transitionArgs]
        transitionArgs = [o(type=arg[0].strip(), text=arg[1].strip()) for arg in transitionArgs]
        startTransitionState = [arg.text for arg in transitionArgs if arg.type=='when'][0] # should only be one of them
        endTransitionState   = [arg.text for arg in transitionArgs if arg.type=='so'][0] # should only be one of them
        startTransitionState = name2instance[startTransitionState]
        endTransitionState   = name2instance[endTransitionState]
        guards=[]
        for guardtext in [arg.text for arg in transitionArgs if arg.type=='if']:
            guards+=["helpers.buildGuard(\"%s\")"%guardtext]
        for guardtext in [arg.text for arg in transitionArgs if arg.type=='unless']:
            guards+=["lambda:not helpers.buildGuard(\"%s\")()"%guardtext]
        actions=[]
        for actiontext in [arg.text for arg in transitionArgs if arg.type=='then']:
            actions+=["helpers.buildAction(\"%s\")"%actiontext]
            # log(actiontext)
            # log(eval("helpers.buildAction(\"%s\")"%actiontext,globals(),locals()))
        if len(guards) is 0:
            guards=["m.true"]
        actions="[%s]"%",".join(actions)
        guards ="[%s]"%",".join(guards)
        # and finally... create the transition
        spec+="""
    t(%s,%s,%s,%s)""" % (startTransitionState, guards, actions, endTransitionState)
    print(spec)
    return spec

def run():
    with open('test_script.yaml', 'r') as file:
        the.script=file.read()

    precompile()
    compile().run()