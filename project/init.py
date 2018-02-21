# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:

# note on imports
# import module            # means you must reference classes from module as module.class
# import module as mo      # means you must reference classes from module as mo.class 
# from module import class # means you must reference classes from module as class
# We should avoid name conflicts so we can use "from" imports for cleaner looking code
from machine import * # imports all class definitions to be used later. doesn't actually run anything.
from base import * # other stuff we might add that doesn't yet have a 'category' we'd designate a whole file for.
from spec import * # contains specs that __main__ will run based on whether @ok is placed before function definition.