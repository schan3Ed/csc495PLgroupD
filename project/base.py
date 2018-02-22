# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random

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