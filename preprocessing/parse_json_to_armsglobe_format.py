#!usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import os
HERE = os.path.abspath(os.path.dirname(__file__))
import subprocess as sp
import logging
import coloredlogs
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s --- %(filename)s --- %(levelname)s --- %(message)s")
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
file_handler = logging.FileHandler(filename = 'log.txt')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
coloredlogs.install(level="INFO")

def printer(inputfile):
    with open(inputfile,"r") as fh:
        j = json.load(fh)
        for k, v in j.items():
            univ_name = v["university"]
            del v["university"]
            v["lon"] = v["long"]
            del v["long"]
            print({univ_name: v})


def sorted_file_generator(filename):
    head_proc = sp.Popen(["head",
                          "-n",
                          "1",
                               filename],
                               stdout=sp.PIPE)
    yield head_proc.stdout.readline().decode('utf-8').strip()
    proc = sp.Popen(["tail",
                     '-n',
                     '+2',
                     filename], stdout=sp.PIPE)
    proc2 = sp.Popen(["sort", "-t,", "-u", "-k1,1"],
                     stdin=proc.stdout,
                     stdout=sp.PIPE)
    while True:
        line = proc.stdout.readline()
        if line:
            yield line.decode('utf-8').strip()
        else:
            break



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description="""
                    parse json to desired format.
                    """)
    parser.add_argument("--version", action='version', version='1.0')
    parser.add_argument("--infile",
                        default=os.path.join(HERE, "../result.csv"),
                        help="list of input files name")
    args = parser.parse_args()
    tempfile = os.path.join(HERE, "../result2.csv")
    tempjson = os.path.join(HERE, "../result2.json")
    logger.debug("going to output {}".format(tempfile))
    with open("result2.csv", "w") as tempfh:
        for l in sorted_file_generator(args.infile):
            tempfh.write(l + "\n")
    json_writer = sp.Popen(["csvjson", "-k", "university", tempfile],
                           stdout=sp.PIPE)
    with open(tempjson, "w") as jsonfh:
        for l in json_writer.stdout.readline().decode('utf-8'):
            jsonfh.write(l)

    printer(tempjson)
