BASIC APARTMENT LISTING SCRAPER
===============================

* Uses BeautifulSoup to scrape seattle craigslist apartment listings
* When run from the command line returns the number of results (<= 100) and a dictionary including information for the first listing
* Since location data is no longer included on the front page, the location data is only lodaded (by following the link) for the first item in the list
