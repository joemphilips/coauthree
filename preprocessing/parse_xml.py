#!usr/bin/env python
# -*- coding: utf-8 -*-
from xml.etree import ElementTree as ET


def parse(filename="./medline16n0417.xml"):
    parser = ET.iterparse(filename)

    for event, element in parse:
        if element.tag == "Affiliation":
            print(element.content)

if __name__ == '__main__':
    parse()
