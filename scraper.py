#!/usr/bin/env python

from __future__ import unicode_literals
import requests
import io
from bs4 import BeautifulSoup
import sys


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

    if not search_parameters:
        raise ValueError("No valid keywords")

    response = requests.post("http://seattle.craigslist.org/search/apa",
                             data=search_parameters)
    if response.ok:
        return response.text, response.encoding
    else:
        raise IOError("Problem with craigslist query or response")


def read_search_results():
    """Return results as if from request_apartments_from_craigslist, but
    using the file apartments.html instead"""
    resultsfile = io.open("apartments.html", "rb")
    return resultsfile.read(), "utf-8"


def parse_source(html):
    return BeautifulSoup(html)


def extract_listings(parsed_page):
    container_criterion = {'class': 'row'}
    link_criterion = {'class': 'hdrlnk'}
    price_criterion = {'class': 'price'}

    data_dictionaries = []
    for listing in parsed_page.find_all(attrs=container_criterion):
        link_element = listing.find('a', attrs=link_criterion)
        price_element = listing.find('span', attrs=price_criterion)
        size_string = price_element.next_sibling.strip(' \n-/')
        data_dictionary = {'link': link_element['href'],
                           'description': link_element.string.strip(),
                           'price': price_element.string.strip(),
                           'size': size_string
                           }
        data_dictionaries.append(data_dictionary)

    return data_dictionaries


def add_location(data_dictionary):
    """Since location information is no longer provided on the main listings,
    Follow the link on a listing (dictionary) you are interested in and add
    location information to it"""
    location_criterion = {'data-longitude': True, 'data-latitude': True}
    response = requests.get("http://seattle.craigslist.org" +
                            data_dictionary['link'])
    parsed_listing = parse_source(response.text)
    location_node = parsed_listing.find(attrs=location_criterion)
    location = {key: location_node.attrs.get(key, '')
                for key in location_criterion}
    data_dictionary['location'] = location


if __name__ == '__main__':
    import pprint
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        raw_text = read_search_results()[0]
    elif len(sys.argv) > 1:
        raise ValueError("The only command-line argument allowed is 'test'")
    else:
        raw_test = request_apartments_from_craigslist(query="Magnolia",
                                                      bedrooms=2,
                                                      maxAsk=2000,
                                                      housing_type=1)[0]

    parsed_page = parse_source(raw_text)
    listings = extract_listings(parsed_page)
    print len(listings)
    add_location(listings[0])
    pprint.pprint(listings[0])
