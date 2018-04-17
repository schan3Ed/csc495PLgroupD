# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
from init import *
from base import *
import the

# ---------------------------------------
if __name__ == "__main__":
    # the.config='../config/bartok_script.yaml'
    # the.config='../config/spades_script.yaml'
    rseed()
    compiler.run()
    # bartok.run()
