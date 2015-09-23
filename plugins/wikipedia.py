#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Searches wikipedia and returns first sentence of article
Scaevolus 2009"""

import wikipedia #gh/goldsmith/Wikipedia
import re
import requests
import urllib
from lxml import etree

from cloudbot import hook
from cloudbot.util import formatting

# security
parser = etree.XMLParser(resolve_entities=False, no_network=True)

api_prefix = "http://en.wikipedia.org/w/api.php"
search_url = api_prefix + "?action=opensearch&format=xml"
random_url = api_prefix + "?action=query&format=xml&list=random&rnlimit=1&rnnamespace=0"

paren_re = re.compile('\s*\(.*\)$')

wikipedia_re = re.compile('(?<=(?:en\.wikipedia\.org/wiki/))([\x21\x22\x24-\x3b\x3d\x3f-\x5a\x5c\x5e-\x7a\x7e]+)(#[\x21-\x22\x24-\x3b\x3d\x3f-\x5a\x5c\x5e-\x7a\x7e]+)?') #Finds an en-WP URL

def find_section(page, title):
    """Workaround for bug with .section(section_title) method"""
    
    if page.section(title) is None:
        res = title + 'Edit'
    else:
        res = title
    return page.section(res)

def get_page_summary(x):
    """Finds a summary for the article or section linked, up to the first period, exclamation mark or question mark"""
    
    try:
        page = wikipedia.WikipediaPage(title=urllib.request.url2pathname(x.group(1))) # Attempts to find the page in Wikipedia
    except wikipedia.exceptions.DisambiguationError as e:
        page = wikipedia.WikipediaPage(title=e.options[1]) # Chooses the first option if it's a disambiguation
    except wikipedia.exceptions.PageError:
        page = "404" # Returns a page not found error if it wasn't found

    if page == "404":
        out = "Page not found!"
    elif x.group(2): # If a section was found in the url:
        section_name = re.sub("_", " ", x.group(2)[1:]) # Removes octothorpe the section title
        section_sentence = re.compile('[^.!?]+[.!?]') # Regex to find summary
        sentence = find_section(page, section_name) # Gets section text
        section_text = section_sentence.search(sentence).group(0) # Finds summary in section text
        out = 'Section \x02' + x.group(2)[1:] + '\x02 from \x02' + page.title + '\x02 :: ' + section_text + ' ...' # Formatted message
    else:
        page_sentence = re.compile('[^.!?]+[.!?]') # Regex to find summary
        out = '\x02' + page.title + "\x02 :: " + page_sentence.search(page.summary).group(0) + ' ...' # Formatted message with summary
    return out

@hook.regex(wikipedia_re) #I believe this works
def wikipedia_url(match):
    return get_page_summary(match)

@hook.command("wiki", "wikipedia", "w")
def wiki(text):
    """wiki <phrase> -- Gets first sentence of Wikipedia article on <phrase>."""

    try:
        request = requests.get(search_url, params={'search': text.strip()})
        request.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        return "Could not get Wikipedia page: {}".format(e)
    x = etree.fromstring(request.text, parser=parser)

    ns = '{http://opensearch.org/searchsuggest2}'
    items = x.findall(ns + 'Section/' + ns + 'Item')

    if not items:
        if x.find('error') is not None:
            return 'Could not get Wikipedia page: %(code)s: %(info)s' % x.find('error').attrib
        else:
            return 'No results found.'

    def extract(item):
        return [item.find(ns + i).text for i in
                ('Text', 'Description', 'Url')]

    title, desc, url = extract(items[0])

    if 'may refer to' in desc:
        title, desc, url = extract(items[1])

    title = paren_re.sub('', title)

    if title.lower() not in desc.lower():
        desc = title + desc

    desc = ' '.join(desc.split())  # remove excess spaces
    desc = formatting.truncate(desc, 200)

    return '{} :: {}'.format(desc, requests.utils.quote(url, ':/%'))
