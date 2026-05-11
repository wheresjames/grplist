#!/usr/bin/python3

import os
from setuptools import setup

def readConfig(fname):
    cfg = {}
    with open(fname) as f:
        for line in f:
            parts = line.strip().replace("\t", " ").split(" ")
            k = parts.pop(0).strip()
            if not k:
                continue
            cfg[k] = " ".join(parts).strip()
    return cfg

here = os.path.abspath(os.path.dirname(__file__))

cfg = readConfig(os.path.join(here, 'grplist', 'PROJECT.txt'))

required = ['name', 'version', 'description', 'url', 'author', 'email', 'license']
missing = [k for k in required if k not in cfg]
if missing:
    raise SystemExit(f"PROJECT.txt is missing required fields: {', '.join(missing)}")

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()
if not long_description:
    long_description = cfg['description']

setup(
    name=cfg['name'],
    version=cfg['version'],
    description=cfg['description'],
    url=cfg['url'],
    author=cfg['author'],
    author_email=cfg['email'],
    license=cfg['license'],
    packages=[cfg['name']],
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
