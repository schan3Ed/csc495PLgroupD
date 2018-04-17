# vim: set filetype=python ts=4 sw=2 sts=2 expandtab:
import sys, re, traceback, time, random, json, copy
import colors
import base
import machine

def init():
    global script
    global load
    global autoplay
    global config
    script="../config/bartok_script.yaml"
    load=machine.Machine.payload
    autoplay=False
    config=None
init()