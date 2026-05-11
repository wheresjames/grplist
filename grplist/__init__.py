
import os
from .grplist import *


def _load_config(fname):
    cfg = {}
    try:
        with open(fname) as f:
            for line in f:
                parts = line.strip().replace("\t", " ").split(" ")
                k = parts.pop(0).strip()
                if not k:
                    continue
                cfg[k] = " ".join(parts).strip()
    except FileNotFoundError:
        raise ImportError(f"grplist package metadata file not found: {fname}")
    return cfg


_project = _load_config(os.path.join(os.path.dirname(__file__), 'PROJECT.txt'))
__version__ = _project.get('version', '0.0.0')
__author__ = _project.get('author', '')
