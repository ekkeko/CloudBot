from bs4 import BeautifulSoup
import requests
from cloudbot import hook


site_url = 'http://www.conversationstarters.com/generator.php'


@hook.command("question", autohelp=False)
def question(text):

    r = requests.get(site_url)
    
    parsed = BeautifulSoup(r.text)
    question = parsed.body.find('div',attrs={'id':'random'})
    if question:
        return question.text
    else:
        return 'failed to fetch question'
