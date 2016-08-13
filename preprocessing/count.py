#!usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging
import pycountry
import coloredlogs
import googlemaps
import os
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s --- %(filename)s --- %(levelname)s --- %(message)s")
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

file_handler = logging.FileHandler(filename = 'log.txt')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
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
    country_to_info = {}
    with open(file1, 'r') as f:
        for l in f:
            # since some capitals or countries includes ", "
            l = l.replace(', ', '. ')

            symbol, _, _, country_name, _, _, capital, lat, lon = \
                l.split(",")[0:9]

            country_to_info[symbol] = \
                country_info(capital, lat, lon.strip())

    logger.debug(country_to_info)
    return country_to_info


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


def _airport_mapping(filename, granularity="city"):
    """get position inforation from airport table
    Args:
        file1: str file path for data downloaded from Amano-giken
        granularity: if you want lat and long for the city in which
            partidular airport exists. than this option should be `city`
            otherwise, it should be `country`
    Returns:
        dict:
            key (str): official country alpha2 symbol, e.g. JA for japan
                or city name, depends on args
            value (tuple): latitude and langitude.
    """
    if granularity not in ("city", "country"):
        raise TypeError("arg `granularity` should be `city` or `country`")

    if granularity == "country":
        longname_to_alpha2 = {}
        for country in pycountry.countries:
                longname_to_alpha2[country.name.upper()] = country.alpha2

    place_info = {}  # lat and lng for that place.
    with open(filename) as fh:
        for l in fh:
            l = l.strip()

            try:
                city, country_name, lng1, lng2, lng3, _, lat1, lat2, lat3 = \
                    l.split(":")[3:12]
            except ValueError:
                logger.exception("could not unpack {} ".format(l))
                raise
            try:
                lng = float(lng1) + float(lng2)/60 + float(lng3)/3600
            except TypeError:
                logger.exception("could not {}:{}:{} convert to float".
                                 format(lng1, lng2, lng3))
                raise
            lat = float(lat1) + float(lat2)/60 + float(lat3)/3600

            if lng == 0.0 or lat == 0.0:
                continue
            if granularity == "country":
                try:
                    country_symbol = longname_to_alpha2[country_name]
                except KeyError:
                    continue
                place_info[country_symbol] = (str(lat), str(lng))
            if granularity == "city":
                place_info[city] = (str(lat), str(lng))
            else:
                logger.exception("granularity {} is not good "
                                 .format(granularity))
                raise ValueError
    logger.info("""length of countris which succeed to parse was {} """.
                format(len(place_info)))
    return place_info


def is_country_in_string(countryobj, string):
    """see if there is country name in string"""
    for names in [countryobj.name,
                  countryobj.alpha3]:
        if re.search(" " + names + r"[,|\.|\s]", string):
            return True
    return False


def _header():
    return ",".join([
        "#countris",
        "#capital:latitude:longitude",
        "#original Affiliation tag info"
    ])


def replace_country_name(Affiliationfile, key=None, table=None,
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
                     in list(paycountry.countries)]

    if google:
        for g in _google_mapping(key, Affiliationfile):
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


def _is_city_in_string(city, string):
    if re.search(r"\s" + city.upper() + r"[\.|\s|,]", string):
        return True
    return False


# @profile
def replace_city_name(Affiliationfile, possible_cities,
                      table, country_table, print_header=False):
    """
    Args:
        Affiliationfile (str): original input file path
        possible_cities (list): string of cities you want to consider
        table (dict): value returned by ``_airport_mapping``
        country_table (dict): value returned by ``mapping``

    Yields:
        str: tab delimited info from Affiliationfile, e.g.
            JA:US,Tokyo:lat:lon,Washington D.C.:lat:lon,
    """
    if print_header:
        yield _header()

    with open(Affiliationfile) as fh:
        for i, l in enumerate(fh):

            if i % 1000 == 1:
                logger.info("finished parsing {} files".format(i))

            l = l.strip()
            affil = re.split(r'[,|\.|\s]', l.split("|||")[-1].upper())
            descripted_city = {c for c in possible_cities if c in affil}

            if len(descripted_city) > 1:
                logger.debug("""there was more than 1 city in file {} line {}
                            and that is {} !!
                            """.format(Affiliationfile, i, affil))
            elif not descripted_city:
                logger.debug("""there was no city info in file {} line {}
                            and that is {} !!
                            """.format(Affiliationfile, i, affil))
                possible_countries = get_possible_countries()
                descripted_countries = {c for c in possible_countries if c in affil}
                for coun in descripted_countries:
                    yield "|||".join([l, coun, "|||".join(country_table[coun])])
                continue

            for c in descripted_city:
                try:
                    yield "|||".join([l, c, "|||".join(table[c])])
                except KeyError:
                    logger.info("no city info in table for {} ".format(c))
                    logger.debug("key of table was {} and \n\n\n "
                                 "descripte city was {} "
                                 .format(table.keys(), descripted_city))
                    continue


def get_possible_cities(filename):
    cities = []
    with open(filename, 'r') as fh:
        for l in fh:
            city = l.split(":")[3]
            cities.append(city)
    return cities


def get_possible_countries():
    return set(c.name for c in pycountry.countries)


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

    parser.add_argument("--source", "-s", nargs="?",
                        choices=["google", "airport", "asti"],
                        type=str,
                        help="""source from which you want to use for getting
                                lattitude and longitude

                                google: use google api, you need to specify API key
                                    with --key option.
                                airport: GlobalAirportDatabaseFile
                                asti: downloaded from Amano-Giken
                             """)

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

        if args.source == "asti":
            country_mapping_table = mapping(os.path.join(HERE,
                                                 "../asti-dath2706wc/h2706world_utf8.csv"))
            result = replace_country_name(inf, table=country_mapping_table)
        elif args.source == "google":
            with open(args.key) as keyfh:
                key = keyfh.read()
            result = replace_country_name(inf, key=key, google=True)
        elif args.source == "airport":
            source_file = os.path.join(HERE, "../data/GlobalAirportDatabase",
                                             "GlobalAirportDatabase.txt")
            table = _airport_mapping(source_file)
            possible_cities = get_possible_cities(source_file)
            country_mapping_table = mapping(os.path.join(HERE,
                                                 "../asti-dath2706wc/h2706world_utf8.csv"))
            result = replace_city_name(inf, possible_cities, table=table,
                                       country_table=country_mapping_table)
        else:
            logger.error("please specify source of latitude and latitude with"
                         "--source")

        with open(outfile, "w") as outfh:
            for r in result:
                outfh.write(r + "\n")


