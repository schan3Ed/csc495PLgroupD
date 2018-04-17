# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
# yaml install instructions: Run pycharm as administrator, open terminal window/view, and execute "pip3 install pyyaml"
import sys, re, traceback, time, random, json, yaml, copy, inspect
from machine import *
from base import o
import helpers
import operator
import ast
from types import MethodType
import the
import colors
from functools import partial

# This is a class. Think of instances of this class as a pointer to an immutable object which belongs to some other dictionary/object variable.
# In this module, the other dictionary/object variable will almost always be the.load or a value that the.load contains
# if type(e)==expr then:
#   e.get() returns the actual immutable value (which in some cases, could be a mutable list)
#   e.set(val) sets the immutable value to val by altering the source/obj/dictionary that originally contained the immutable value 
expr=Machine.PayloadItem

# each of these return a map where keys are function names and values are the actual functions
def guards():  return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('g__')})
def actions(): return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('a__')})
def shared():  return o.convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('s__')})

# these are command builders
# they are functions that loop through helper functions, and return the corresponding lambda function that is meant to be executed at run time 
def buildAction(text):
    return buildCommand(text, actions())
def buildGuard(text):
    command = buildCommand(text, guards(), forcematch=False)
    return command if command else lambda:True
def buildCommand(text, commands, forcematch=None):
    forcematch = True if forcematch is None else forcematch
    try:
        if(text is 'log'):
            return lambda:log(the.load) or True
        for key,func in commands.itemsbykey(reversed=True):
            if matchesFunction(text,key):
                return func(getArgs(text, key))
    except Exception as e:
        if(forcematch): raise e
    return None

# these are functions used by the command builders
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

# this function is similar to a command builder, except it is responsable for using the shared helper functions
# possibly nested within arguments for guard and action commands. This function builds an expr (see top of page)
def getExpr(text):
    # class Expr(o):
    # 	def get(i): return i.obj[i.key]
    # 	def set(i,val): i.obj[i.key]=val
    val=buildCommand(text,shared(),forcematch=False)
    if text in the.load.keys():
        val = expr(obj=the.load, key=text)
    elif val is not None:
        return expr(key=val)
    else:
        try:
            val = ast.literal_eval(text)
            val = expr(key=val)
        except Exception:
            val = expr(key=text)
    return val

# this is how the game maker can prompt for input.
# autoplay just returns a random choice from options.
def choose(options, prompt = None, autoplay=None):
    prompt = prompt or ''
    autoplay = autoplay or False
    if autoplay:
        choice = random.choice(options)
        print(colors.negative("You chose %s from %s"%(choice, options)))
    else:
        choice = None
        while choice is None:
            try:
                if prompt != '' and prompt[-1]!=' ':
                    prompt += ' '
                print("%s(type a number then hit Enter)" % prompt)
                print("\n".join(["%i: %s" % (idx,option) for idx, option in enumerate(options)]))
                number = int(input("enter a number: "))
                if number < 0 or number >= len(options):
                    raise IndexError("INVALID INPUT: that number is not an option")
                choice = options[number]
                print(colors.negative("YOU CHOSE %s" % choice))
            except Exception as e:
                print(colors.red('Invalid Input. Try again.'))
    the.load.choice=choice
    return choice

def getColor(card): pass #TODO

def getSuit(card):
    suitmap=o(
        h='hearts',
        s='spades',
        c='clubs',
        d='diamonds'
    )
    return suitmap[card[-1]]

def getRank(card):
    try:
        val = card[:-1]
        val = ast.literal_eval(val)
        if val > 10:
            rankMap=o({
                    '11':'jack',
                    '12':'queen',
                    '13':'king'
                }
            )
            val = rankMap[str(val)]
        return val
    except Exception as e:
        return None

# #################################################
# ############### HELPER FUNCTIONS ################
# #################################################
# Helper functions define the syntax of the language used for RULES in the game maker's script
# Helper functions take strings in place of X's in their function names, and return a lambda to perform some operation or return some value at run time
# helper function format: A__pBB__C
# A is either g for guard commands, a for action commands, or s for shared commands (which are usually just accessors used to enhance the getExpr method)
# B is the priority of the function
#   function priority determines the order in which the parse tree is constructed in the event that more than one helper function matches input
#   higher priorities become higher nodes in the parse tree
#       for example: if user input was "size of draw deck" and the following functions existed:
#           a__p01__X_of_X
#           a__p02__size_of_X
#       the input would evaluate to lambda: a__p02__size_of_X(['draw deck'])
#       instead of                  lambda: a__p01__X_of_X(['size','draw deck'])
# C pattern used to match user input.
#   if C is preceeded with 'll__'
#       it means that it's parse tree is left associative. LR is default
#       it is especially useful for the previous example X_of_X if the user were to chain it
#           ie '__ll' would make the input 'size of hand of player1' become:
#               this:       a__p01__X_of_X(['size','hand of player1'])
#               instead of: a__p01__X_of_X(['size of hand','player1'])
#
# NOTE: every helper function takes a single argument, a list of strings.
#   The number of X's (only capital) in the function determines the number strings it should accept 
#   and also the order in which those strings appear. For examples, see previous examples in this comment.
# NOTE: parse tree behavior of functions with matching priorities is undefined.
#   Functions with matching priorities should theoretically never conflict given proper syntax/grammer
# NOTE: functions of the same type (the value of A in the function name), are never checked simultaneously, therefore priorties will never conflict

# WHERE HELPER FUNCTIONS ARE USED IN THE LANGUAGE
# Only used in the RULES section of the game maker's script. 
# 'if'/'unless' followed by text will parse that text as a guard function/ 
# 'then' followed by text will parse that text as an action function.
# shared functions (A=='s') are never the root operation of a parse tree, rather, they are used by other functions, often via the getExpr function 

#
#                GUARD HELPER FUNCTIONS
# #################################################
def g__p09__for_every_player_X(args): # similar to the action version of this function, but only returns true if the evaluated guard returns true for all players
    x1=args[0]
    playerGuards = [re.sub(r"\bplayer\b", player, x1) for player in the.script.players]
    playerGuards = [buildGuard(guard) for guard in playerGuards]
    return lambda:False not in [guard() for guard in playerGuards]

def g__p09__for_any_player_X(args): # similar to for_every_player guard, but returns true if at least 1 guards evaluate to true
    x1=args[0]
    playerGuards = [re.sub(r"\bplayer\b", player, x1) for player in the.script.players]
    playerGuards = [buildGuard(guard) for guard in playerGuards]
    return lambda: True in [guard() for guard in playerGuards]

def g__p07__X_or_X(args):
    x1,x2 = args
    isTrue = lambda x: g__p05__X_is_true([x])()
    return lambda: isTrue(x1) or isTrue(x2)

def g__p06__X_and_X(args):
    x1,x2 = args
    isTrue = lambda x: g__p05__X_is_true([x])()
    return lambda: isTrue(x1) and isTrue(x2)

def g__p05__X_is_false(args):
    isTrue = lambda x: g__p05__X_is_true([x])()
    return lambda:not isTrue(args)

def g__p05__X_is_true(args):
    x1 = args[0]
    x1 = buildCommand(x1, guards(), forcematch=False)
    x1 = x1 or args[0]
    x1 = getExpr(x1)
    return lambda: x1() if callable(x1) else bool(x1.get()) and x1.get()!=[]
    
def g__p05__X_is_empty(args):
    x1 = args[0]
    x1 = getExpr(x1)
    return lambda: len(x1.get()) == 0

def g__p04__X_isnt_X(args):
    return lambda: not g__p04__X_is_X(args)

def g__p04__X_is_X(args):
    x1,x2 = args
    x1 = getExpr(x1)
    x2 = getExpr(x2)
    return lambda:x1.get()==x2.get()

#
#                ACTION HELPER FUNCTIONS
# #################################################

def a__p10__for_every_player_X_where_X(args):
    x1,x2=args
    isTrue = lambda x: g__p05__X_is_true([x])()
    forEveryPlayer = lambda x: a__p09__for_every_player_X(x)()
    return lambda: forEveryPlayer(x1) if isTrue(x2) else None

def a__p09__for_every_player_X(args): # builds and calls an action to perform once for every player by calling buildAction and providing one version of the text each time, but with the word 'player' replaced with player names like 'player1' 'player2' etc
    x1=args[0]
    playerActions = [re.sub(r"\bplayer\b", player, x1) for player in the.script.players]
    playerActions = [buildAction(action) for action in playerActions]
    return lambda:[action() for action in playerActions]

# x1 is player
# x2 is draw deck
# x3 is where card is drawn into. likely player's hand
# x4 are the player's card options. likely the players hand
# x5 is where the chosen card is placed. ie 'face deck'
# x6 is the condition for a valid card. if false after player choice, reprompt user for choice
def a__p06__X_draws_from_X_into_X_or_plays_from_X_into_X_where_X(args):
    def fun(args=args):
        x1,x2,x3,x4,x5,x6 = args
        isTrue = lambda x: g__p05__X_is_true([x])()
        play = lambda x: choose(getExpr(x4).get()+["draw from %s"%x1], autoplay=the.autoplay)
        # backupEnvironment = copy.deepcopy(the.load)
        play()
        while not isTrue(x6) and 'draw' not in the.load.choice:
            print(colors.red("The requirement '%s' was not met. Try again."%x6))
            play()
        if 'draw' in choice:
            getExpr(x5).get().append(getExpr(x2).get().pop())
        else:
            getExpr(x4).get().remove(choice)
            getExpr(x5).get().append(choice)
    return fun

def a__p05__X_draws_from_X_into_X_or_plays_from_X_into_X(args):
    def fun(args=args):
        x1, x2, x3, x4, x5 = args
        choice = choose(getExpr(x4).get()+["draw from %s"%x1], autoplay=the.autoplay)
        if 'draw' in choice:
            getExpr(x5).get().append(e2.get().pop())
        else:
            getExpr(x4).get().remove(choice)
            getExpr(x5).get().append(choice)
    return fun

def a__p04__X_plays_from_X_into_X_where_X(args):
    def fun(args=args):
        x1,x2,x3,x4 = args
        isTrue = lambda x: g__p05__X_is_true([x])()
        play = lambda x: choose(getExpr(x2).get()+["draw from %s"%x1], autoplay=the.autoplay)
        backupEnvironment = copy.deepcopy(the.load)
        play()
        while not isTrue(x4):
            print(colors.red("The requirement '%s' was not met. Try again."%x4))
            the.load=backupEnvironment
            backupEnvironment = copy.deepcopy(the.load)
            play()
        getExpr(x2).get().remove(the.choice)
        getExpr(x3).get().append(the.choice)
    return fun
    # return lambda: play([x1,x2,x3]) if isTrue(x4) else None

def a__p03__X_plays_from_X_into_X(args):
    def fun(args=args):
        x1,x2,x3 = args
        e1=getExpr(x1)
        e2=getExpr(x2)
        e3=getExpr(x3)
        choice = choose(e2.get(), autoplay=the.autoplay)
        e2.get().remove(choice)
        e3.get().append(choice)
    return fun

def a__p00__transfer_X_cards_from_X_to_X(args):
    x1, x2, x3 = args
    x1 = getExpr(x1)
    x2 = getExpr(x2)
    x3 = getExpr(x3)
    # lists are mutable so x3.get() is okay. but in most cases, x3.set would be necessary to update the actual payload value
    return lambda: [x3.get().append(x2.get().pop()) for i in range(x1.get())]

def a__p00__increment_X(args): 
    def fun():
        x = getExpr(args[0])
        x.set(x.get()+1)
    return fun

# x1 is a string for a load key who's value is a string for a player
# EXAMPLE
# x1 == 'current player'
# the.load['current player'] == 'player 3'
# the.script.players = ['player 1', 'player 2','player 3']
# after the action takes place, the.load['current player']=='player 1'
def a__p01__reverse_rotate_X(args):
    x1 = args[0]
    x1 = getExpr(x1)
    p = the.script.players
    return lambda: x1.set(p[(p.index(x1.get())-1) % len(p)]) # decrements index but cycles at boundary

def a__p00__rotate_X(args):
    x1 = args[0]
    x1 = getExpr(x1)
    p = the.script.players
    return lambda: x1.set(p[(p.index(x1.get())+1) % len(p)]) # increments index but cycles at boundary

def a__p01__announce_X_without_new_line(args):
    x = args[0]
    isQuoted = bool(x[0] is '"' and x[-1] is '"')
    x = x[1:-1] if isQuoted else getExpr(x)
    return lambda: print(x if isQuoted else x.get(), end='')

def a__p01__with_the_color_X_announce_X(args):
    x1,x2 = args
    if x1 in colors.COLORS:
        color = lambda x:partial(colors.color, fg=x1)(str(x))
    elif x1 in colors.STYLES:
        color = lambda x:partial(colors.color, style=x1)(str(x))
    isQuoted = bool(x2[0] is '"' and x2[-1] is '"')
    x2 = x2[1:-1] if isQuoted else getExpr(x2)
    return lambda: print(color(x2 if isQuoted else x2.get()))

def a__p00__X_is_now_X(args):
    x1,x2 = args
    x1=getExpr(x1)
    x2=getExpr(x2)
    return lambda: x1.set(x2.get())

def a__p00__reset_X(args): pass # sets x1 to it's initial value set in script


def a__p00__shuffle_X(args):
    x = args[0]
    x = getExpr(x)
    return lambda: shuffle(x.get())

def a__p00__announce_X(args):
    x = args[0]
    isQuoted = bool(x[0] is '"' and x[-1] is '"')
    x = x[1:-1] if isQuoted else getExpr(x)
    return lambda: print(x if isQuoted else x.get())

#
#                SHARED HELPER FUNCTIONS
# #################################################
# make sure getters that return a card (aka any instance from any list)
# have lower priorities than functions that
# return descriptive values of that card (unless said value is in fact another card)



def s__p05__top_card_of_X(args):
    x1=args[0]
    return lambda: expr(key=getExpr(x1).get()[-1])

def s__p06__rank_of_X(args):
    x1=args[0]
    return lambda: expr(key=getRank(getExpr(x1).get()))

def s__p06__suit_of_X(args):
    x1=args[0]
    return lambda: expr(key=getSuit(getExpr(x1).get()))

def s__p06__size_of_X(args):
    return lambda:expr(key=len(getExpr(args[0]).get()))

def s__p01__ll__X_of_X(args):
    x1,x2 = args
    x2 = getExpr(x2)
    def fun(x1=x1, x2=x2):
        if x1 in x2.get():
            return expr(obj=x2.get(), key=x1)
        else:
            while 'obj' in getExpr(x2.get()):
                x2 = getExpr(x2.get())
                if x1 in x2.get():
                    return expr(obj=x2.get(), key=x1)
        raise Exception("'%s' does not exist in any object"%str(x1))
    return fun