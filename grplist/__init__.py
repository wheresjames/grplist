
import os
from . grplist import *

def loadConfig(fname):
    with open(fname) as f:
        lines = f.readlines()
        for line in lines:
            parts = line.strip().replace("\t", " ").split(" ")
            k = parts.pop(0).strip()
            globals()["__%s__"%k] = " ".join(parts).strip()

loadConfig(os.path.join(os.path.dirname(__file__), 'PROJECT.txt'))

