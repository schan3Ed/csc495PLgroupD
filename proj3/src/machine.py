# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
from base import *

# ---------------------------------------

debugmode = True
allowloadlogging = True
def log(msg):
    if debugmode:
        if msg is not Machine.payload or allowloadlogging:
            print(colors.magenta(str(msg)))
        else:
            print(colors.magenta('<<<< log hit >>>>'))

def asLambda(i, txt):
    def methodsOf(i):
        return [s for s in i.__dir__() if s[0] is not "_"]

    for one in methodsOf(i):
        txt = re.sub(one, 'z.%s()' % one, txt)
    txt = "lambda z: " + txt
    code = eval(txt)
    # e.g. print("> ",code(i))


# ---------------------------------------
# <BEGIN>
class State(o):
    tag = ""

    def __init__(i, name, machine):
        cut = len(name)-len(i.tag)
        i.name = name[0:cut]
        i._trans = []
        i._machine = machine

    def id(i):
        return " => %s" % i.name

    def trans(i, guards, actions, destination):
        i._trans += [Transition(i, guards, actions, destination)]

    def step(i):
        for t in i._trans:
            if False not in [val for val in map(lambda f:f(),t.guards)]:
                if t.actions is not None and len(t.actions)>0:
                    for action in t.actions:
                        action()
                i._universalOnExit()
                i.onExit()
                t.destination._universalPreparePayload()
                t.destination.preparePayload()
                t.destination._universalOnEntry()
                t.destination.onEntry()
                return t.destination
        return i

    def _universalPreparePayload(i):
        """Do not override.
        This function will update payloads for ALL states before every 
        call to preparePayload. Overriding will cause that state
        to use it's function instead of the universal one.
        """
        Machine.payload.system.count += 1
        Machine.payload.path += i.id() # re.sub(r'[^a-zA-Z0-9_]*', '', i.name + ' '
        if i.tag == NestedState.tag: 
            Machine.payload.path += '{ '
        e = State.FSMLimit
        if Machine.payload.system.count > e.STEP_LIMIT: 
            raise e("Cannot exceed %s executed states" % e.STEP_LIMIT)

    def _universalOnEntry(i):
        """Do not override.
        This function will run for ALL states before every 
        call to onEntry. Overriding will cause that state
        to use it's function instead of the universal one.
        """
        # print("%s  => " % i.name, end='') # DEBUG
        pass

    def _universalOnExit(i):
        """Do not override.
        This function will run for ALL states before every 
        call to onExit. Overriding will cause that state
        to use it's function instead of the universal one.
        """
        if i.tag == NestedState.tag:
            Machine.payload.path += '} '
        pass

    def preparePayload(i): pass
    def onEntry(i): pass
    def onExit(i): pass

    def quit(i): # Returning indicates it's the last state of the machine
        return False

    class FSMLimit(Exception): STEP_LIMIT = 10000

class NestedState(State):
    tag = "#"

    def __init__(i, name, machine):
        super().__init__(name,machine)
        i._submachine = None

    def onEntry(i):
        super(NestedState, i).onEntry()
        if i._submachine:
            i._submachine.run()

class Start(State):
    tag = '|>'

class Exit(State):
    tag = "."

    def quit(i):
        return True

    def onExit(i):
        return i


# ---------------------------------------
class Transition(o):
    def __init__(i, _current, guards, actions, destination):
        for k,v in locals().items(): i.__dict__[k]=v
        del i.__dict__['i']
        # if i.action: i.action._i=i


# ---------------------------------------
class Machine(o):
    """Maintains a set of named states.
       Creates new states if its a new name.
       Returns old states if its an old name."""
    payload = o(system=o(count=0), path='')

    def __init__(i, name):
        i.all = {}
        i.name = name
        i.start = None

    def isa(i, x):
        if isinstance(x, State):
            return x
        for k in isa(State):
            if k.tag and contains(x, k.tag):
                return k(x, i)
        return State(x, i)

    def state(i, x):
        i.all[x] = y = i.all[x] if x in i.all else i.isa(x)
        if isinstance(y,Start): i.start = y
        return y

    def trans(i, here, guards, actions, destination):
        i.state(here).trans(guards, actions, i.state(destination))

    def run(i):
        state = i.start
        state._universalPreparePayload()
        state.preparePayload()
        state._universalOnEntry()
        state.onEntry()
        while True:
            state = state.step()
            if state.quit():
                break
        state._universalOnExit()
        return state.onExit()


    def unlikely(i): return random.random() < .25
    def likely(i): return random.random() < .75
    def maybe(i):    return random.random() < 0.5
    def true(i):     return True

    class PayloadItem(o):
        def get(i):
            if 'obj' in i: return i.obj[i.key]
            elif callable(i.key):
                val = i.key()
                if type(val) is bool:
                    return val
                if isinstance(val, type(i)):
                    return val.get()
            else:          return i.key
        def set(i,val):
            if 'obj' in i and 'key' in i:
                i.obj[i.key]=val
            elif callable(i.key):
                i.key().set(val)

class SubMachine(Machine):
    def __init__(i, name, parentMachine):
        super().__init__(name,most=most)
        i.parentMachine = parentMachine

# ---------------------------------------
def make(m, fun):
    fun(m, m.state, m.trans)
    return m

# END>