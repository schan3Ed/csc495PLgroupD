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
def guards():  return convert({k: v for k, v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('g__')})

def actions(): return convert({k : v for k,v in inspect.getmembers(helpers, inspect.isfunction) if k.startswith('a__')})

# re.sub https://stackoverflow.com/questions/31005138/replace-regex-matches-in-a-string-with-items-from-a-list-in-order

def buildAction(text):
	for key,func in actions().items():
		if matchesFunction(text,key):
			func(getArgs(text,key))
	

def matchesFunction(text,fString):
	if re.compile("^"+getFRegStr(fString)+"$").match(text) is not None:
		return True
	return False

def getArgs(text, fString):
	regStr = getFRegStr(fString)
	args = re.compile(regStr).findall(text)
	return args
	
def getFRegStr(fString):
	regstr = re.compile("[ag]__p[0-9]+__(.*)").search(fString).group(1)
	regstr = regstr.replace('_',' ')
	regstr = re.sub(r"\bX\b", "(.*)", regstr)
	return regstr
    # for key, val in actions().items():
        # TODO: return lambda function thats calls the correct helper function and passes the correct load variables. 

# helper function format: A__pBB__C
# A is either g for guard or a for action
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

def g__p01__X_is_true(args):
    x = args[0][0]
    return bool(x)

def a__p01__X_is_now_X(args):
    x1=args[0][0]
    x2=args[0][1]
    load[x1] = x2

def a__p02__X_asdf_X(x1, x2):
   pass