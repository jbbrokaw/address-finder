"""
code that tests the Craigslist scraper functions defined in binheap.py

can be run with py.test
"""
from __future__ import unicode_literals

import pytest  # used for the exception testing
from bs4 import BeautifulSoup
from scraper import request_apartments_from_craigslist
from scraper import read_search_results
from scraper import parse_source
from scraper import extract_listings
from scraper import add_location
from copy import copy


def test_request_apartments_from_craigslist():
    #Test keywords are required
    with pytest.raises(ValueError) as err:
        request_apartments_from_craigslist()
        assert "No valid keywords" in err.data

    response, encoding = request_apartments_from_craigslist(query="Queen Anne")
    assert encoding == "utf-8"
    assert isinstance(response, unicode)
    assert "Queen Anne" in response  # This is a little iffy, but should work


def test_read_search_results():
    response, encoding = read_search_results()
    assert encoding == "utf-8"
    assert isinstance(response, unicode)
    assert "Queen Anne" in response  # I searched Queen Anne to make the file


def test_parse_source():
    with pytest.raises(TypeError):
        parse_source()
    with pytest.raises(TypeError):
        parse_source(None)

    response, encoding = read_search_results()
    parsed_page = parse_source(response)
    assert isinstance(parsed_page, BeautifulSoup)
    assert "Queen Anne" in parsed_page.prettify()


def test_extract_listings():
    with pytest.raises(TypeError):
        extract_listings()
    with pytest.raises(AttributeError):  # Could change this but eh
        extract_listings(None)

    response, encoding = read_search_results()
    parsed_page = parse_source(response)
    listings = extract_listings(parsed_page)
    assert isinstance(listings, list)
    assert isinstance(listings[0], dict)
    testdict = listings[0]
    assert isinstance(testdict['size'], unicode)
    assert "br" in testdict['size']
    assert isinstance(testdict['description'], unicode)
    assert isinstance(testdict['link'], unicode)
    assert "html" in testdict['link']
    assert isinstance(testdict['price'], unicode)
    assert '$' in testdict['price']
    assert testdict['price'].strip("$").isdigit()


def test_add_location():
    with pytest.raises(TypeError):
        add_location()
    with pytest.raises(TypeError):
        add_location(None)

    response, encoding = read_search_results()
    parsed_page = parse_source(response)
    listings = extract_listings(parsed_page)
    olddict = copy(listings[0])
    add_location(listings[0])
    newdict = listings[0]
    assert len(newdict) == len(olddict) + 1  # Added a single entry, "location"
    for key in olddict:
        assert olddict[key] == newdict[key]

    with pytest.raises(KeyError):
        olddict['location']

    assert isinstance(newdict['location'], dict)
    locationdict = newdict['location']
    assert 'data-latitude' in locationdict
    assert 'data-longitude' in locationdict
    # The following lines should not raise exceptions
    float(locationdict['data-latitude'])
    float(locationdict['data-longitude'])



