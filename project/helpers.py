# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml, copy, inspect
from base import *
from machine import *
from actions import *
from compiler import *
import helpers
import colors

# maps of helper function names and the actual function
def guards():  return o.convert({k: v for k, v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('g__') or k.startswith('s__')})

def actions(): return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('a__') or k.startswith('s__')})

# re.sub https://stackoverflow.com/questions/31005138/replace-regex-matches-in-a-string-with-items-from-a-list-in-order

def execAction(text):
	if(text is 'log'): return lambda:log(load) or True
	for key,func in actions().items():
		if matchesFunction(text,key):
			func(getArgs(text, key, execAction))
	return None

def execGuard(text):
	if(text is 'log'): return lambda:log(load) or True
	for key,func in guards().items():
		if matchesFunction(text,key):
			func(getArgs(text, key, execGuard))
	return None
	

def matchesFunction(text,fString):
	if re.compile("^"+getFRegStr(fString)+"$").match(text) is not None:
		return True
	return False

def getArgs(text, fString, mapFunc):
	regStr = getFRegStr(fString)
	args = [mapFunc(text) or getLiteral(text) for text in re.compile(regStr).findall(text)[0]]
	return args
	
def getFRegStr(fString):
	regstr = re.compile("[ag]__p[0-9]+__(.*)").search(fString).group(1)
	regstr = regstr.replace('_',' ')
	regstr = re.sub(r"\bX\b", "(.*)", regstr)
	return regstr

def getLiteral(text): 
	return o(obj=load,key=text) # default behavior
	# Connor's TODO: return parent object and key value so function can manipulate the load

# helper function format: A__pBB__C
# A is either g for guard commands, a for action commands, or s for shared commands
# B is the priority of the function, which determines the order in which is it checked and matched to user input (lower values first)
#   for example: if user input was "size of draw deck" and the following functions existed:
#       a__p01__size_of_X
#       a__p02__size_X
#   the input would evaluate to lambda: a__p01__size_of_X(load['draw deck'])
#   instead of                  lambda: a__p02__size_X(load['of draw deck'])
# C pattern used to match user input.
#
# NOTE: the number of X's in the function determines the number of parameters it should accept, 
# in addition to where those parameters should be expected from user input
# Note: order of functions with matching priorities is undefined


def g__p01__for_every_player(args): pass # similar to the action version of this function, but only returns true if the evaluated guard returns true for all players 

def g__p01__for_any_player(args): pass # similar to for_every_player guard, but returns true if at least 1 guards evaluate to true 

def g__p01__X_is_true(args):
    x1 = args[0]
    return bool(x1.obj[x1.key])==True

def g__p01__X_is_empty(args): pass


def a__p01__for_every_player(args): pass # builds and calls an action to perform once for every player by calling execAction and providing one version of the text each time, but with the word 'player' replaced with player names like 'player1' 'player2' etc 

def a__p01__transfer_X_from_X_to_X(args): pass # transfers the top x1 number of items in list x2 into the list x3

def a__p01__increment_X(args): pass

def a__p01__rotate_X(args): pass # X will be a number from 0 to numPlayers-1... increment it but set back to zero if equal to numPlayers (not a global value... must count players field from compiled script)

def a__p01__X_is_now_X(args):
    x1=args[0]
    x2=args[1]
    x1.obj[x1.key] = x2.obj[x2.key]

def a__p01__reset_X(args): pass # sets x1 to it's initial value set in script

def a__p01__announce_X(args): pass # print x1


def s__p01__size_of_X(args): pass # returns the size of x1

def s__p02__X_of_X(args): pass # returns a tuple, first entry is the object (such as one of the players), the second containing the key of the object (like "hand")