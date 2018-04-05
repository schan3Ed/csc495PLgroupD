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
            hidden: no
    PLAYERS :
        - player1
        - player2
        - player3
        - player4
    """

    script = precompile(script)
    compile(script).run()