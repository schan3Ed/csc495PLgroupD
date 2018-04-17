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
    
def initload():
    if 'decks' in the.script.__dict__:
        for deck in the.script.decks:
            the.load[deck.name] = deck.contents
    if 'players' in the.script.__dict__:
        for player in the.script.players:
            if 'player attributes' in the.script.__dict__:
                the.load[player] = copy.deepcopy(the.script['player attributes'])
                the.load[player].name=player
    if 'game attributes' in the.script.__dict__:
            for key,val in the.script['game attributes'].items():
                the.load[key] = val

def buildspec():
    # log(the.script)
    # desides the spec's variable names within the spec function, 
    # and the corresponding phrasing in which the game maker would use to identify said states
    name2instance = o.convert({
        "starting"             : "start",
        "new game is started"  : "gamestart",
        "new turn is started"  : "turnstart",
        "new round is started" : "roundstart",
        "game is finished"     : "end"
    })

    spec = """
def spec(m, s, t):"""
    
    # defines the states available for use by the game maker
    for identifier, instanceName in name2instance.items():
        if instanceName=='start': identifier = "%s|>"%identifier
        if instanceName=='end'  : identifier = "%s." %identifier
        spec+="""
    %s = s("%s")""" % (instanceName, identifier)
    
    # sanitize quotes in script. also allows for the use of quotes in the language such as literal strings in the '...anounce...' helper function
    the.script.rules = [re.sub("\"","\\\"",rule) for rule in the.script.rules]
    # for each rule, builds the rule into something like this:
    # t(gamestart,[helpers.buildGuard("for every player score of player is 1")],[helpers.buildAction("for every player score of player is now 2")],gamestart)
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
            guards+=["lambda: helpers.buildGuard(\"%s\")()"%guardtext]
        for guardtext in [arg.text for arg in transitionArgs if arg.type=='unless']:
            guards+=["lambda:not helpers.buildGuard(\"%s\")()"%guardtext]
        actions=[]
        for actiontext in [arg.text for arg in transitionArgs if arg.type=='then']:
            actions+=["lambda: helpers.buildAction(\"%s\")()"%actiontext]
        if len(guards) is 0:
            guards=["m.true"]
        actions="[%s]"%",".join(actions)
        guards ="[%s]"%",".join(guards)
        # and finally... create the transition
        spec+="""
    t(%s,%s,%s,%s)""" % (startTransitionState, guards, actions, endTransitionState)
    log(spec)
    return spec

# specifies which script to compile, compiles it, and runs it
def run():
    with open('bartok_script.yaml', 'r') as file:
        the.script=file.read()

    precompile()
    compile().run()