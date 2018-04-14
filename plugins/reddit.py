from datetime import datetime
import re
import random
import asyncio
import functools
from urllib.parse import urlparse

import praw
import requests

from cloudbot import hook
from cloudbot.util import timeformat, formatting


reddit_re = re.compile(r'.*(((www\.)?reddit\.com/r|redd\.it)[^ ]+)', re.I)

base_url = "http://reddit.com/r/{}/.json"
short_url = "http://redd.it/{}"


def format_output(item, show_url=False):
    """ takes a reddit post and returns a formatted string """
    item["title"] = formatting.truncate(item["title"], 70)
    item["link"] = short_url.format(item["id"])

    raw_time = datetime.fromtimestamp(int(item["created_utc"]))
    item["timesince"] = timeformat.time_since(raw_time, count=1, simple=True)

    item["comments"] = formatting.pluralize(item["num_comments"], 'comment')
    item["points"] = formatting.pluralize(item["score"], 'point')

    if item["over_18"]:
        item["warning"] = " \x02NSFW\x02"
    else:
        item["warning"] = ""

    if show_url:
        return "\x02{title} : {subreddit}\x02 - {comments}, {points}" \
               " - \x02{author}\x02 {timesince} ago - {link}{warning}".format(**item)
    else:
        return "\x02{title} : {subreddit}\x02 - {comments}, {points}" \
               " - \x02{author}\x02, {timesince} ago{warning}".format(**item)


@hook.regex(reddit_re)
def reddit_url(match, bot):
    url = match.group(1)
    if "redd.it" in url:
        url = "http://" + url
        response = requests.get(url)
        url = response.url + "/.json"
    if not urllib.parse.urlparse(url).scheme:
        url = "http://" + url + "/.json"

    # the reddit API gets grumpy if we don't include headers
    headers = {'User-Agent': bot.user_agent}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return
    data = r.json()
    if type(data) == list:
        item = data[0]["data"]["children"][0]["data"]
    elif type(data) == dict:
        #item = data["data"]["children"][random.randint(0,9)]["data"]
        return

    return format_output(item)


@asyncio.coroutine
@hook.command(autohelp=False)
def reddit(text, bot, loop):
    """<subreddit> [n] - gets a random post from <subreddit>, or gets the [n]th post in the subreddit"""
    id_num = None
    headers = {'User-Agent': bot.user_agent}

    if text:
        # clean and split the input
        parts = text.lower().strip().split()

        # find the requested post number (if any)
        if len(parts) > 1:
            url = base_url.format(parts[0].strip())
            try:
                id_num = int(parts[1]) - 1
            except ValueError:
                return "Invalid post number."
        else:
            url = base_url.format(parts[0].strip())
    else:
        url = "http://reddit.com/.json"

    try:
        # Again, identify with Reddit using an User Agent, otherwise get a 429
        inquiry = yield from loop.run_in_executor(None, functools.partial(requests.get, url, headers=headers))
        if inquiry.status_code != 200:
            return "r/{} either does not exist or is private.".format(text)
        data = inquiry.json()
    except Exception as e:
        return "Error: " + str(e)
    data = data["data"]["children"]

    # get the requested/random post
    if id_num is not None:
        try:
            item = data[id_num]["data"]
        except IndexError:
            length = len(data)
            return "Invalid post number. Number must be between 1 and {}.".format(length)
    else:
        item = random.choice(data)["data"]

    return format_output(item, show_url=True)

@hook.on_start
def reddit_login(bot):
    global reddit_instance 
    reddit_instance = praw.Reddit(client_id=bot.config.get("api_keys", {}).get("reddit_client_id", None),
            client_secret=bot.config.get("api_keys", {}).get("reddit_client_secret", None),
            user_agent=bot.config.get("api_keys", {}).get("reddit_user_agent", None),
            username=bot.config.get("api_keys", {}).get("reddit_username", None),
            password=bot.config.get("api_keys", {}).get("reddit_password", None))
            
def is_image(url):
    parsed = urlparse(url)
    splitted = parsed.path.split('.')
    if len(splitted) > 1 and splitted[1] in ['jpg', 'gifv', 'gif', 'jpeg', 'png'] or 'gfycat' in parsed.netloc:
        return True
    else:
        return False

def get_image(subname):

    MAX_IMAGE_LIST = 50
    LIMIT_NO_IMG = 50

    sub = reddit_instance.subreddit(subname)

    submlist = []

    for index, submission in enumerate(sub.hot(limit=900)):
        if not submission.is_self and is_image(submission.url):
            submlist.append(submission)

        if len(submlist) >= MAX_IMAGE_LIST:
            break

        # give up if couldn't find any images in the first LIMIT_NO_IMG submissions
        if index > LIMIT_NO_IMG and len(submlist) == 0:
            break

    if submlist:
        return random.choice(submlist)
    else:
        raise praw.exceptions.PRAWException('Could not find image')

def get_displayline(submission):
    return '{} ({} - {} - {} ) {}'.format(submission.url, submission.subreddit_name_prefixed, submission.title, submission.shortlink, ' \x0304NSFW' if submission.over_18 else '')

@hook.command('image')
def reddit_random_image_search(text):
    try:
        subm = get_image(text)
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)
    
@hook.command('bork')
def random_bork_search():
    sub = random.choice(['woof_irl', 'woofbarkwoof', 'supershibe', 'rarepuppers', 'dogpictures', 'doggos', 'surpriseddogs'])
    try:
        subm = get_image(sub)
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)

@hook.command('meow','miau')
def random_meow_search():
    sub = random.choice(['catsstandingup', 'catpictures', 'kitty', 'cats', 'catsinbusinessattire', 'meow_irl'])
    try:
        subm = get_image(sub)
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)

@hook.command('omnomnom','nom')
def random_nom_search():
    try:
        subm = get_image('gifrecipes')
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)
