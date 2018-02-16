#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import subprocess as sp
from ast import literal_eval

def syscmd (cmd):
    out = sp.check_output(cmd, shell = True).split('\n')
    return [x for x in out if len(x) > 0]

def getfilepath (filename, pathkey):
    cmd = 'locate ' + filename
    out = syscmd(cmd)
    filepath = ''
    filepath = next(x for x in out if pathkey in x)
    if len(filepath) == 0:
        print ("Warning: couldn't locate file " + filename)
    return filepath

def getfilepaths (pathkey):
    cmd = 'ls ' + pathkey
    return syscmd(cmd)

def literalReadFile (filepath):
    with open(filepath, 'r') as f:
        s = f.read()
    return literal_eval(s) ## returns python data

def readJsonFile (filepath):
    with open(filepath) as json_file:
        d = json.load(json_file)
    return d ## returns a dictionary

def saveJsonFile (filepath, d): # 'd' is a dictionary
    with open(filepath, 'w') as json_file:
        json.dump(d, json_file, indent=4, sort_keys=True)
