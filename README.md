BASIC APARTMENT LISTING SCRAPER
===============================

* Uses BeautifulSoup to scrape seattle craigslist apartment listings
* From an individual craigslist listing, gets latitude & longitude data
* Uses that lat & lng data to use the Google maps api to return a nicely formatted street address
* When run from the command line prints a dictionary including information for the first listing, from both Craigslist and Google
* Since location data is no longer included on the Craigslist front page, the location data is only lodaded (by following the link) for the first item in the list
* Note also that Craigslist seems to ignore the bodies of post requests to its search page (the form seems to be doing complicated stuff obscured by some javascript)
* I avoided this problem by doing a get request with search parameters in the url
