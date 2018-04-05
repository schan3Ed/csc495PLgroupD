# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random
import colors

def rseed(seed=1):
    random.seed(int(seed))

def about(f):
    print("\n-----| %s |-----------------" % f.__name__)
    if f.__doc__:
        print("# " + re.sub(r'\n[ \t]*', "\n# ", f.__doc__))

def indentedlist(list, indent=0):
    indentStr = ''.join(["\t" for i in range(0,indent)])
    return indentStr + str("\n"+indentStr).join(map(lambda item:str(item), list))

TRY = FAIL = 0

def ok(f=None):
    global TRY, FAIL
    if f:
        try:
            TRY += 1; about(f); f(); print("# pass");
        except:
            FAIL += 1; print(traceback.format_exc());
        return f
    else:
        print("\n# %s TRY= %s ,FAIL= %s ,%%PASS= %s" % (
            time.strftime("%d/%m/%Y, %H:%M:%S,"),
            TRY, FAIL,
            int(round((TRY - FAIL) * 100 / (TRY + 0.001)))))

def shuffle(lst):
    random.shuffle(lst)
    return lst

def contains(all, some):
    return all.find(some) != -1


def kv(d):
    """Return a string of the dictionary,
       keys in sorted order,
       hiding any key that starts with '_'"""
    return '(' + ', '.join(
        ['%s: %s' % (k, d[k])                    for k in sorted(d.keys()) if k[0] != "_"] +
        ['%s: %s' % (k, d[k].__class__.__name__) for k in sorted(d.keys()) if k[0] == "_"]
        ) + ')'


def isa(k, seen=None):
    assert isinstance(k, type), "superclass must be 'object'"
    seen = seen or set()
    if k not in seen:
        seen.add(k)
        yield k
        for sub in k.__subclasses__():
            for x in isa(sub, seen):
                yield x

                class Thing(object):
    def __repr__(i):
        return i.__class__.__name__ + kv(i.__dict__)


class o(Thing):
    def __init__(i, **dic): i.__dict__.update(dic)

    def __getitem__(i, x): 
        return i.__dict__[x]

    def __setitem__(i, key, value):
        i.__dict__[str(key)] = value

    def keys(i):
        return i.__dict__.keys()

    def values(i):
        return i.__dict__.values()
        
"""Recursively converts dictionaries into objects"""
def convert(x):
    if type(x) == dict:
        for key,val in x.items():
            x[key] = convert(val)
        obj = o()
        obj.__dict__.update(x)
        return obj
    if type(x) == list:
        for idx, val in enumerate(x):
            x[idx] = convert(val)
    return x