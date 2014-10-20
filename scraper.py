#!/usr/bin/env python

from __future__ import unicode_literals
import urllib
import urllib2
import io


def request_apartments_from_craigslist(
        query=None,
        pets_cat=None,
        pets_dog=None,
        housing_type=None,
        minAsk=None,
        maxAsk=None,
        bedrooms=None,
        bathrooms=None,
        minSqft=None,
        maxSqft=None):
    """Return Craigslist's response to a query with the provided parameters"""
    search_parameters = {key: value for key, value in locals().items()
                         if value is not None}

    encoded_request = urllib.urlencode(search_parameters)
    print encoded_request

    try:
        conn = urllib2.urlopen("http://seattle.craigslist.org/search/apa",
                               encoded_request)
        print conn.headers
        out_file = io.open("apartments.html", "wb")
        out_file.write(conn.read())
    except:
        raise

if __name__ == '__main__':
    request_apartments_from_craigslist(query="Magnolia",
                                             bedrooms=2,
                                             maxAsk=2000,
                                             housing_type=1)
