# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml, copy
from base import *
from machine import *
from actions import *
from bartok import *
import colors
import helpers

load = Machine.payload

debugmode = True

def log(msg):
    if debugmode:
        print(colors.magenta(str(msg)))

def yaml2json(text):
    text = json.dumps(yaml.load(script), sort_keys=True, indent=2)
    text = json.loads(text)
    return text

def precompile(script):
    script = json.dumps(yaml.load(script), sort_keys=True, indent=2)
    script = str(script).lower()
    script = re.sub(r'\bnull\b', '[]', script)
    script = json.loads(script)
    script = o.convert(script)
    for deck in script.decks:
        if not isinstance(deck.contents, list):
            deck.contents = deck.contents.split(' ')
    return script

def compile(script):
    initload(script)
    specStr = buildspec(script)
    exec(specStr, globals(), globals())
    return make(Machine("CUSTOM_GAME"), globals()['spec'])
    # return make(Machine("CUSTOM_GAME"), spec_bartok)
    
# OLD PAYLOAD STRUCTURE (log load during runtime to see new payload structure)
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

def initload(script):
    if 'decks' in script.__dict__:
        for deck in script.decks:
            load[deck.name] = deck.contents
    if 'players' in script.__dict__:
        for player in script.players:
            load[player] = deck.contents
            if 'player attributes' in script.__dict__:
                load[player] = copy.deepcopy(script['player attributes'])
    if 'game attributes' in script.__dict__:
            for key,val in script['game attributes'].items():
                load[key] = val

def buildspec(script):
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
    
    spec+= """
    def chooseAndPlay():
        # log(load)
        chooseCard()
        while not playIsValid():
            invalidMessage()
            chooseCard()
        play()

    turnstart.onEntry = chooseAndPlay
    """

    for rule in script.rules:
        transitionArgs = re.sub(r"\b(when|if|then|unless|so)\b", "-\\1:", rule).split('-')[1:]
        transitionArgs = [arg.split(':') for arg in transitionArgs]
        transitionArgs = [o(type=arg[0].strip(), text=arg[1].strip()) for arg in transitionArgs]
        startTransitionState = [arg.text for arg in transitionArgs if arg.type=='when'][0] # should only be one of them
        endTransitionState   = [arg.text for arg in transitionArgs if arg.type=='so'][0] # should only be one of them
        startTransitionState = name2instance[startTransitionState]
        endTransitionState   = name2instance[endTransitionState]
        guards=[]
        for guardtext in [arg.text for arg in transitionArgs if arg.type=='if']:
            guards+=["lambda:helpers.execGuard(\"%s\")"%guardtext]
        for guardtext in [arg.text for arg in transitionArgs if arg.type=='unless']:
            guards+=["lambda:not helpers.execGuard(\"%s\")"%guardtext]
        actions=[]
        for actiontext in [arg.text for arg in transitionArgs if arg.type=='then']:
            actions+=["lambda:helpers.execAction(\"%s\")"%actiontext]
        if len(guards) is 0:
            guards=["m.true"]
        actions="[%s]"%",".join(actions)
        guards ="[%s]"%",".join(guards)
        # and finally... create the transition
        spec+="""
    t(%s,%s,%s,%s)""" % (startTransitionState, guards, actions, endTransitionState)
    return spec

def run():
    script=""
    with open('test_script.yaml', 'r') as file:
        script=file.read()#.replace('\n', '')
    # an alternative to a "X_of_X" or "size_of_X" helper, I may match that same function name to the input "X's X"
    # so a function like size of X can still match against the input "size of hand" AND "hand's size"

    script = precompile(script)
    print(compile(script).__dict__)
    compile(script).run()