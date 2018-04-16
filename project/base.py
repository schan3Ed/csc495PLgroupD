# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random, json, copy
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

def isa(k, seen=None):
    assert isinstance(k, type), "superclass must be 'object'"
    seen = seen or set()
    if k not in seen:
        seen.add(k)
        yield k
        for sub in k.__subclasses__():
            for x in isa(sub, seen):
                yield x

def kv(d):
    """Return a string of the dictionary,
       keys in sorted order,
       hiding any key that starts with '_'"""
    return '(' + ', '.join(
        ['%s: %s' % (k, d[k])                    for k in sorted(d.keys()) if k[0] != "_"] +
        ['%s: %s' % (k, d[k].__class__.__name__) for k in sorted(d.keys()) if k[0] == "_"]
        ) + ')'

class CustomEncoder(json.JSONEncoder):
    def default(i, obj):
        if isinstance(obj, JsonSerializable):
            return json.loads(obj.to_json())
        if hasattr(obj, '__call__'):
            return 'function ' + obj.__name__
        return json.JSONEncoder.default(i, obj)

class JsonSerializable(object):
    def to_json(i):
        try:
            return json.dumps(i.__dict__, sort_keys=True, indent=8, cls = CustomEncoder)
        except Exception:
            return str(i.__dict__)

    def __repr__(i):
        return i.to_json()

    def __str__(i):
        return i.to_json()

class o(JsonSerializable):
    def __init__(i, *args, **dic):
        for arg in args:
            i.update(arg)
        i.update(dic)

    def __getitem__(i, x):
        return i.__dict__[str(x)]

    def __setitem__(i, key, value):
        i.__dict__[str(key)] = value

    def __iter__(i):
        return iter(i.__dict__)

    def update(i,val):
        if type(val) is o:
            return i.__dict__.update(val.__dict__)
        else:
            return i.__dict__.update(val)

    def items(i):
        return i.__dict__.items()

    def itemsbykey(i, reversed=None):
        reversed = reversed or False
        return sorted(i.items(), reverse=reversed)

    def itemsbyvalue(i, reversed=None):
        reversed = reversed or False
        sorted(i.items(),key=lambda item:item[1], reverse=reversed)

    def keys(i):
        return i.__dict__.keys()

    def values(i):
        return i.__dict__.values()

    def sorted(i):
        sorted(i.__dict__)

    """Recursively converts dictionaries into o"""
    @staticmethod
    def convert(x):
        if type(x) == dict:
            for key, val in x.items():
                x[key] = o.convert(val)
            obj = o()
            obj.__dict__.update(x)
            return obj
        if type(x) == list:
            for idx, val in enumerate(x):
                x[idx] = o.convert(val)
        return x

class Card(o):
    def __init__(self, name, suit, rank, fun=None):
        self.fun = fun or (lambda: None)
        self.name = str(name)
        self.suit = str(suit)
        self.rank = str(rank)