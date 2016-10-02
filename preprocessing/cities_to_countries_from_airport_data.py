#!usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
HERE = os.path.abspath(os.path.dirname(__file__))
filepath = os.path.join(HERE, "../data/GlobalAirportDatabase/GlobalAirportDatabase.txt")

result = {}
with open(filepath) as fh:
    for l in fh:
        city = l.split(":")[3]
        country = l.split(":")[4]
        result[city] = country

    print(json.dumps(result))
