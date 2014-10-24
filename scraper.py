#!/usr/bin/env python

from __future__ import unicode_literals
import requests
import io
from bs4 import BeautifulSoup
import sys
import json
from pprint import pprint


def request_apartments_from_craigslist(
        query=None,
        pets_cat=None,
        pets_dog=None,
        minAsk=None,
        maxAsk=None,
        bedrooms=None,
        bathrooms=None,
        minSqft=None,
        maxSqft=None):
    """Return Craigslist's response to a query with the provided parameters"""
    search_parameters = {key: value for key, value in locals().items()
                         if value is not None}

    pprint(search_parameters)

    if not search_parameters:
        raise ValueError("No valid keywords")

    response = requests.get("http://seattle.craigslist.org/search/see/apa",
                            params=search_parameters)

    if response.ok:
        return response.text, response.encoding
    else:
        raise IOError("Problem with craigslist query or response")


def read_search_results():
    """Return results as if from request_apartments_from_craigslist, but
    using the file apartments.html instead"""
    resultsfile = io.open("apartments.html", "r", encoding="utf-8")
    return resultsfile.read(), "utf-8"


def parse_source(html):
    return BeautifulSoup(html)


def extract_listings(parsed_page):
    container_criterion = {'class': 'row'}
    link_criterion = {'class': 'hdrlnk'}
    price_criterion = {'class': 'price'}

    for container_element in parsed_page.find_all(attrs=container_criterion):
        link_element = container_element.find('a', attrs=link_criterion)
        price_element = container_element.find('span', attrs=price_criterion)
        size_string = price_element.next_sibling.strip(' \n-/')
        listing = {'link': link_element['href'],
                   'description': link_element.string.strip(),
                   'price': price_element.string.strip(),
                   'size': size_string}
        yield listing


def add_location(listing):
    """Since location information is no longer provided on the main listings,
    Follow the link on a listing (dictionary) you are interested in and add
    location information to it"""
    location_criterion = {'data-longitude': True, 'data-latitude': True}
    response = requests.get("http://seattle.craigslist.org" +
                            listing['link'])
    parsed_listing = parse_source(response.text)
    location_node = parsed_listing.find(attrs=location_criterion)
    if location_node:
        location = {key: location_node.attrs.get(key, '')
                    for key in location_criterion}
    else:  # They didn't provide location; I'm just going to fake it
        location = {"data-latitude": 48.112493, "data-longitude": -122.233332}
    listing['location'] = location


def format_google_request_parameters(location):
    """Return valid request parameters (dictionary) to send to google,
    given scraped location dictionary"""
    lat = location["data-latitude"]
    lng = location["data-longitude"]
    latlng = "%s,%s" % (lat, lng)
    return {'latlng': latlng, 'sensor': 'false'}


def ask_google_for_address(listing):
    """make a reverse geocoding lookup using the google api"""
    url = "http://maps.googleapis.com/maps/api/geocode/json"
    request_params = \
        format_google_request_parameters(listing["location"])
    resp = requests.get(url, params=request_params)
    data = json.loads(resp.text)
    if data['status'] != 'OK':
        raise IOError("Problem with Google request")
    return data


def get_google_data_from_file():
    """fake a reverse geocoding lookup using the google api (read from file)"""
    stored_file = io.open("address.txt", "r")
    data = json.load(stored_file)
    return data


def find_best_address(goog_data):
    best_record = None
    for record in (goog_data['results']):
        if 'street_address' in record['types']:
            best_record = record
            break
    # Could go thru looking for 'locality' or 'postal code'. I'm just taking
    # the first instead, since they seem to be consistently sorted
    if not best_record:
        best_record = goog_data['results'][0]
    if 'formatted_address' in best_record:
        return best_record['formatted_address']
    else:
        raise IOError("Couldn't parse Google response")


def add_google_address(listing, address):
    """Add address (str/unicode) as the address in listing"""
    listing['address'] = address


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "test":
        raw_text = read_search_results()[0]
        parsed_page = parse_source(raw_text)
        listing_generator = extract_listings(parsed_page)
        listing = listing_generator.next()
        add_location(listing)
        goog_data = get_google_data_from_file()

    elif len(sys.argv) > 1:
        raise ValueError("The only command-line argument allowed is 'test'")

    else:
        raw_text = request_apartments_from_craigslist(query="Queen Anne",
                                                      bedrooms=2,
                                                      maxAsk=2000)[0]
        parsed_page = parse_source(raw_text)
        listing_generator = extract_listings(parsed_page)
        listing = listing_generator.next()
        add_location(listing)
        goog_data = ask_google_for_address(listing)

        resultsfile = io.open("apartments.html", "w")
        resultsfile.write(parsed_page.prettify())
        resultsfile.close()
        goog_file = io.open("address.txt", "wb")
        json.dump(goog_data, goog_file)
        goog_file.close()

    best_address = find_best_address(goog_data)
    add_google_address(listing, best_address)
    pprint(listing)
