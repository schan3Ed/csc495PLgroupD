# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random, json, copy
import colors
import base
import machine

def init():
    global script
    global load
    global autoplay
    script=""
    load=machine.Machine.payload
    autoplay=True
init()