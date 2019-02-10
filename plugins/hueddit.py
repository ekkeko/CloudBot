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
    return '{} ( {} - {} - {} ) {}'.format(submission.url, submission.subreddit_name_prefixed, submission.title, submission.shortlink, ' \x0304NSFW' if submission.over_18 else '')

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
    sub = random.choice(['gifrecipes','foodporn'])
    try:
        subm = get_image(sub)
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)

@hook.command('quack')
def random_duck_search():
    sub = random.choice(['duck'])
    try:
        subm = get_image(sub)
    except praw.exceptions.PRAWException as e:
        return e
    return get_displayline(subm)
