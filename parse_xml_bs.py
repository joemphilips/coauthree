#!usr/bin/env python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup

def parse(filename):
    with open(filename) as fh:
        bsobj = BeautifulSoup(fh, "lxml")
        bsobj.findAll()
