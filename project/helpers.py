# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml, copy, inspect
from machine import *
import helpers
import operator
import ast
from types import MethodType
import the

script=the.script
# maps of helper function names and the actual function
expr=Machine.PayloadItem

def guards():  return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('g__')})
def actions(): return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('a__')})
def shared():  return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('s__')})
# re.sub https://stackoverflow.com/questions/31005138/replace-regex-matches-in-a-string-with-items-from-a-list-in-order

def buildAction(text):return buildCommand(text, actions())
def buildGuard(text):
    command = buildCommand(text, guards(), forcematch=False)
    return command if command else lambda:True

def buildCommand(text, commands, forcematch=None):
    forcematch = True if forcematch is None else forcematch
    if(text is 'log'):
        return lambda:log(the.load) or True
    for key,func in commands.itemsbykey():
        if matchesFunction(text,key):
            return func(getArgs(text, key))
    if(forcematch):
        raise Exception("Could not build command \"%s\""%text)
    return None

def matchesFunction(text,fString):
    if re.compile("^"+getFRegStr(fString)+"$").match(text) is not None:
        return True
    return False

def getArgs(text, fString):
    search = re.compile("[ags]__p[0-9]+__(ll__)?(.*)").search(fString)
    preOrderTraversal = bool(search.group(1))
    regstr = getFRegStr(fString)
    if preOrderTraversal:
        regstr = "((?:(?!%s).)*)%s"%(regstr[4:regstr.rindex("(.*)")],regstr[4:]) # dont allow identical commands in the first parameter
    args = re.compile(regstr).findall(text)[0]
    args = [args] if type(args) is str else [arg for arg in args]
    return args

def getFRegStr(fString):
    fString = fString.replace('ll__','')
    search = re.compile("[ags]__p[0-9]+__(.*)").search(fString)
    # preOrderTraversal = bool(search.group(1))
    regstr = search.group(1)
    regstr = regstr.replace('_',' ')
    regstr = re.sub(r"\bX\b", "(.*)", regstr)
    # if preOrderTraversal:
    #     regstr = "([^(%s)]*)%s"%(regstr[4:regstr.rindex("(.*)")],regstr[4:])
    return regstr

def getExpr(text):
    # class Expr(o):
    # 	def get(i): return i.obj[i.key]
    # 	def set(i,val): i.obj[i.key]=val
    val=buildCommand(text,shared(),forcematch=False)
    if text in the.load.keys():
        val = expr(obj=the.load, key=text)
    elif val is not None:
        return val()
    else:
        try:
            val = ast.literal_eval(text)
            val = expr(key=val)
        except Exception:
            val = expr(key=text)
    return val

# helper function format: A__pBB__C
# A is either g for guard commands, a for action commands, or s for shared commands
# B is the priority of the function, which determines the order in which is it checked and matched to user input (lower values first)
#   for example: if user input was "size of draw deck" and the following functions existed:
#       a__p01__size_of_X
#       a__p02__size_X
#   the input would evaluate to lambda: a__p01__size_of_X(the.load['draw deck'])
#   instead of                  lambda: a__p02__size_X(the.load['of draw deck'])
# C pattern used to match user input.
#
# NOTE: the number of X's in the function determines the number of parameters it should accept, 
# in addition to where those parameters should be expected from user input
# Note: order of functions with matching priorities is undefined


def g__p01__for_every_player_X(args): # similar to the action version of this function, but only returns true if the evaluated guard returns true for all players
    x1=args[0]
    playerGuards = [re.sub(r"\bplayer\b", player, x1) for player in the.script.players]
    playerGuards = [buildGuard(guard) for guard in playerGuards]
    return lambda:False not in [guard() for guard in playerGuards]

def g__p01__for_any_player_X(args): # similar to for_every_player guard, but returns true if at least 1 guards evaluate to true
    x1=args[0]
    playerGuards = [re.sub(r"\bplayer\b", player, x1) for player in the.script.players]
    playerGuards = [buildGuard(guard) for guard in playerGuards]
    return lambda: True in [guard() for guard in playerGuards]

def g__p06__X_is_X(args):
    x1,x2 = args
    x1 = getExpr(x1)
    x2 = getExpr(x2)
    return lambda:x1.get()==x2.get()


def g__p05__X_is_true(args):
    x1 = args[0]
    x1 = getExpr(x1)
    return lambda:bool(x1.get())

def g__p05__X_is_empty(args):
    x = getExpr(args[0])
    return lambda: len(x) == 0


def a__p01__for_every_player_X(args): # builds and calls an action to perform once for every player by calling buildAction and providing one version of the text each time, but with the word 'player' replaced with player names like 'player1' 'player2' etc
    x1=args[0]
    playerActions = [re.sub(r"\bplayer\b", player, x1) for player in the.script.players]
    playerActions = [buildAction(action) for action in playerActions]
    return lambda:[action() for action in playerActions]



def a__p05__transfer_X_from_X_to_X(args): # transfers the top x1 number of items in list x2 into the list x3
    x1, x2, x3 = args
    x1 = getExpr(x1)
    x2 = getExpr(x2)
    x3 = getExpr(x3)
    def fun():
        for i in range(x1):
            x3.append(x2.pop())
    return fun

def a__p05__increment_X(args): 
    x = getExpr(args[0])
    def fun():
        x += 1
    return lambda: x

def a__p05__rotate_X(args): pass # X will be a number from 0 to numPlayers-1... increment it but set back to zero if equal to numPlayers (not a global value... must count players field from compiled script)

def a__p05__X_is_now_X(args):
    x1,x2 = args
    x1=getExpr(x1)
    x2=getExpr(x2)
    return lambda: x1.set(x2.get())

def a__p05__reset_X(args): pass # sets x1 to it's initial value set in script

def a__p05__announce_X(args):
    x = getExpr(args[0])
    return lambda: print(x)
    # print x1


def s__p05__size_of_X(args): 
    return lambda: len(getExpr(args[0]))
     # returns the size of x1

def s__p05__ll__X_of_X(args):
    x1,x2 = args
    x2 = getExpr(x2)
    if x1 in x2.get():
        return lambda:expr(obj=x2.get(), key=x1)
    raise Exception("'%s' does not exist in any object"%str(x1))


 # returns a tuple, first entry is the object (such as one of the players), the second containing the key of the object (like "hand")