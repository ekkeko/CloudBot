import requests

from cloudbot import hook
from cloudbot.util import formatting

import re
from urllib.parse import urlparse, quote
import json
import requests

api_url = 'https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty'

hnre = re.compile(r'^http[s]?:\/\/news\.ycombinator\.com\/item\?id=[0-9]*$')

@hook.regex(hnre)
def hackernews(match):
    try:
        id = urlparse(match.group(0)).query.split('=')[1]
        r = requests.get(api_url.format(id)).json()
        
        isgdurl = 'http://is.gd/create.php?format=simple&url=' + quote(r['url'],safe='')
        result = requests.get(isgdurl)
        urlshort = result.text
        
        return 'HackerNews: {} - {}'.format(r['title'],urlshort)
        #jsonresult = json.loads(api_url.format(id))
        return jsonresult.title
    except:
        pass