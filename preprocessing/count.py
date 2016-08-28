#!usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
import pycountry
import coloredlogs
import googlemaps
import os
import weakref
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s --- %(filename)s --- %(levelname)s --- %(message)s")
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(filename = 'log.txt')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

coloredlogs.install(level="ERROR")


from collections import namedtuple
country_info = namedtuple('country_info', ["capital", "lat", "lon"])


def mapping(file1):
    """
    Args:
        file1: str file path for data downloaded from Amano-giken
    Returns:
        dict:
            key (str): official country alpha2 symbol, e.g. JA for japan
            value (country_info): namedtuple of ``capital``, ``lat``, ``lon``
    """
    country_to_capital = {}
    with open(file1, 'r') as f:
        for l in f:
            symbol, _, _, country_name, _, _, capital, lat, lon = \
                l.split(",")[0:9]
            country_to_capital[symbol] = \
                country_info(capital, lat, lon.strip())

    logger.debug(country_to_capital)
    return country_to_capital


def _google_mapping(key, inputfile, cachefile="googlemapinfocache"):
    """download information from googlemap
        return value will be same as
    """
    gmaps = googlemaps.Client(key=key)

    # _affilname_2_place = weakref.WeakKeyDictionary()
    _affilname_2_place = {}

    # read cache
    try:
        with open(cachefile, "r") as fh:
            for l in fh:
                affil, place_id, lat, lng = l.strip().split(",")
                _affilname_2_place[affil] = (place_id, lat, lng)
    except EnvironmentError:
        logger.info("there was no cache file {} ".format(cachefile))

    with open(inputfile) as fh:
        for l in fh:
            l = l.strip()
            affil = l.split("|||")[-1]

            if affil not in _affilname_2_place.keys():
                geocode_result = gmaps.geocode(affil)

                if not geocode_result:
                    logger.error("there was no geocode_result for {} ".format(affil))
                    continue
                else:
                    logger.debug("result of geocode was {}".format(geocode_result))

                place_id = geocode_result[0]["address_components"][0]["short_name"]
                lat = geocode_result[0]["geometry"]["location"]['lat']
                lng = geocode_result[0]["geometry"]["location"]['lng']
                _affilname_2_place[affil] = (place_id, str(lat), str(lng))

            yield "|||".join([l, "|||".join(_affilname_2_place[affil])])

        # save to cache
    # with open(cachefile, "w") as fh:
    #     for affil, info in _affilname_2_place.items():
    #         cachefile.write(",".join([affil, info[0], info[1], info[2], "\n"])


def is_country_in_string(countryobj, string):
    """see if there is country name in string"""
    for names in [countryobj.name,
                  countryobj.alpha3]:
        if re.search(" " + names + " ", string):
            return True
    return False


def _header():
    return ",".join([
        "#countris",
        "#capital:latitude:longitude",
        "#original Affiliation tag info"
    ])


def replace_country_name(Affiliationfile, key, table=None,
                         google=False, print_header=False):
    """
    Args:
        Affiliationfile (str): original input file path
        table (dict): value returned by ``mapping``
        key (str): googlemap API key, required only google is True.
        google (bool): use googlemap api or not

    Yields:
        str: tab delimited info from Affiliationfile, e.g.
            JA:US,Tokyo:lat:lon,Washington D.C.:lat:lon,
    """
    if print_header:
        yield _header()

    all_countries = [l
                     for l
                     in list(pycountry.countries)]

    if google:
        for g in  _google_mapping(key, Affiliationfile):
            yield g
        return

    with open(Affiliationfile) as fh:
        for i, l in enumerate(fh):
            l = l.strip()
            affil = l.split("|||")[-1]
            descripted_country = [c
                                  for c
                                  in all_countries
                                  if is_country_in_string(c, affil)]

            if len(descripted_country) > 1:
                logger.debug("""there was more than 1 country in file {} line {}
                            and that is {} !!
                            """.format(Affiliationfile, i, affil))
            elif not descripted_country:
                logger.debug("""there was no country info in file {} line {}
                            and that is {} !!
                            """.format(Affiliationfile, i, affil))
                continue

            country_symbols = [c.alpha2 for c in descripted_country]
            for c in country_symbols:
                try:
                    yield "|||".join([l, c, "|||".join(table[c])])
                except KeyError:
                    logger.info("no country info for {} ".format(c))
                    continue


if __name__ == '__main__':
    HERE = os.path.abspath(os.path.dirname(__file__))
    import argparse
    parser = argparse.ArgumentParser(description="""

    """)
    parser.add_argument("--version", action='version', version='1.0')
    parser.add_argument("inp", nargs='*',
                        help="list of input files name")

    parser.add_argument("outpath", nargs=1,
                        help="output file path")

    parser.add_argument("--google", "-g", nargs="?",
                        type=bool,
                        help="use googlemap api for getting "
                             "lattitude and longitude")

    parser.add_argument("--key", "-k", nargs="?",
                        type=str,
                        help="path of API key for using google map API")

    parser.add_argument('--verbose', '-v', action='count',
                        help="""set this to change debug level
                                -v:   INF0
                                -vv:  DEBUG
                            """)

    args = parser.parse_args()

    for inf in args.inp:
        outfile = os.path.join(args.outpath[0], os.path.splitext(inf)[0] + ".csv")
        logger.info("going to output {} ".format(outfile))
        if not args.google:
            mapping_table = mapping(os.path.join(HERE,
                                                 "asti-dath2706wc/h2706world_utf8.csv"))
            result = replace_country_name(inf, table=mapping_table)
        else:
            with open(args.key) as keyfh:
                key = keyfh.read()
            result = replace_country_name(inf, key=key, google=True)

            print(result)
        with open(outfile, "w") as outfh:
            for r in result:
                outfh.write(r + "\n")


