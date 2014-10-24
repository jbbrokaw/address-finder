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
from scraper import format_google_request_parameters
from scraper import ask_google_for_address
from scraper import add_google_address
from copy import copy
import types


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
    with pytest.raises(AttributeError):
        extract_listings(None).next()

    response, encoding = read_search_results()
    parsed_page = parse_source(response)
    listing_generator = extract_listings(parsed_page)
    assert isinstance(listing_generator, types.GeneratorType)
    testdict = listing_generator.next()
    assert isinstance(testdict, dict)
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
    listing_generator = extract_listings(parsed_page)
    listing = listing_generator.next()
    olddict = copy(listing)
    add_location(listing)
    newdict = listing
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


def test_format_google_request_parameters():
    """This function should return valid request parameters (dictionary)
    to send to google, given scraped location dictionary"""
    with pytest.raises(TypeError):
        format_google_request_parameters()  # listing required

    response, encoding = read_search_results()
    parsed_page = parse_source(response)
    listing_generator = extract_listings(parsed_page)
    listing = listing_generator.next()
    add_location(listing)

    request_params = format_google_request_parameters(listing['location'])
    assert isinstance(request_params, dict)
    assert 'latlng' in request_params
    assert request_params['sensor'] == 'false'


def test_ask_google_for_address():
    """This function should return google's response (dictionary)
    given a listing with location data"""
    with pytest.raises(TypeError):
        ask_google_for_address()  # listing required

    response, encoding = read_search_results()
    parsed_page = parse_source(response)
    listing_generator = extract_listings(parsed_page)
    listing = listing_generator.next()
    add_location(listing)

    goog_data = ask_google_for_address(listing)
    assert isinstance(goog_data, dict)
    assert 'results' in goog_data
    assert isinstance(goog_data['results'], list)
    first_result = goog_data['results'][0]
    assert isinstance(first_result, dict)

    # We are implicitly testing find_best_address() here, too
    assert 'types' in first_result
    assert 'street_address' in first_result['types']
    # I'm more or less assuming the above is the case;
    # google seems to reliably do this
    assert 'formatted_address' in first_result
    assert isinstance(first_result['formatted_address'], unicode)


def test_add_google_address():
    """add_google_address(listing, address) should add address (string) to
    the listing dictionary"""
    with pytest.raises(TypeError):
        add_google_address()
    with pytest.raises(TypeError):
        add_google_address(None)
    with pytest.raises(TypeError):
        add_google_address(None, "123 Fake Street")

    test_listing = {}
    add_google_address(test_listing, "123 Fake Street")
    assert 'address' in test_listing
    assert test_listing['address'] == '123 Fake Street'
