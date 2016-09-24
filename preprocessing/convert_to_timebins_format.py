#!usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import groupby, product
import json
import subprocess

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


def sorted_file_generator(filename):
    with open(filename) as fh:
        for l in fh:
            yield l


def key_function(x):
    try:
        return x.split("|")[12]
    except IndexError:
        logger.debug("could not split {}".format(x))
        raise


def group_by_firstcolumn(filename):
    """group samfile's entry which has same read name
    Rerurns:
        itertools.groupby: which yields tuple of (fistcolumn, whole row)
    """
    key = key_function
    iter = sorted_file_generator(filename)
    return groupby(iter, key=key)


from collections import defaultdict
coauth_count = defaultdict(int)


def coauthor_count(medline_abst, relation="city"):
    """take tab delimeted abstract and

    returns count for coauthor

    Args:
        relation: "city", or "human" returns weight of their relation

    Returns:
        defaultdict:
            key (set): possible combination for city (or human)
            value (int): number of coauthor in that city
    """
    grouped = group_by_firstcolumn(medline_abst)
    for paper_id, items in grouped:

        if paper_id is None:
            continue

        logger.debug("paper_id is {} ".format(paper_id))

        # weight of edge between graph
        if relation == "human":
            list_in_same_paper = [extract_fullname(i) for i in items]
        elif relation == "city":
            list_in_same_paper = [i.split("|")[21] for i in items]
        else:
            raise ValueError

        # 2 element set for authornames
        combies = {tup for tup
                   in product(list_in_same_paper, list_in_same_paper)
                   }
        for i in combies:
            coauth_count[i] += 1

    logger.debug(coauth_count)
    return coauth_count


def extract_fullname(line):
    return ",".join([line.split("|")[21], line.split("|")[18]])


def extract_city(line):
    return line.split("|")[21]


def timebins(filename):
    """return dict for armsglobe compatible style"""
    count = coauthor_count(filename)
    return json.dumps({"timeBins":
        [
            {"data": list(json_entries(count))}
        ]
     })


def json_entries(count):
    for twocity, w in count.items():
        yield json_entry(twocity, w)


def json_entry(twocity, w):
    return {
        "i": twocity[0],
        "wc": "none",
        "e": twocity[1],
        "v": str(w)
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="""

                """)
    parser.add_argument("--version", action='version', version='1.0')
    parser.add_argument("infile",
                        help="input files name")
    args = parser.parse_args()

    print(timebins(args.infile))
