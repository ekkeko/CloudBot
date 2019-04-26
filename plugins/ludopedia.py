import random
import re
import requests
import unidecode

from cloudbot import hook
from cloudbot.util import web, formatting
from urllib.parse import quote


@hook.command("ludopedia")
def ludopedia(text):
    """ludopedia <board game name> -- Looks up <board game name> on https://ludopedia.com.br."""

    if text:
        # clean and split the input
        text = text.lower().strip()
        parts = text.split()

        # if the last word is a number, set the ID to that number
        if parts[-1].isdigit():
            id_num = int(parts[-1])
            # remove the ID from the input string
            del parts[-1]
        else:
            id_num = 1

        text = "-".join(parts)

        # fetch the definitions
        try:
            url = "https://ludopedia.com.br/jogo/"+unidecode.unidecode(text)
            request = requests.get(url)
            request.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            return "Could not get definition: {}".format(e)

        page = request.text

        definitions = re.findall("<div class=\"bloco-sm-content bloco-sm-content-open\" id=\"bloco-descricao-sm\">(.*?)</div>", page, re.DOTALL)

        #definitions = re.findall("< class=\"text-post\">(.*?)</span>", page, re.DOTALL)

        if definitions:
            try:
                definition = definitions[id_num - 1]
                def_text = sanitize(definition)
            except IndexError:
                return 'Não encontrado.'

            short_url = web.try_shorten(url)
            
            output = "[{}/{}] {} - {}".format(id_num, len(definitions), def_text, short_url)
        else:
            output = 'Não encontrei nenhum jogo de tabuleiro com o nome \x02' + text + '\x02.'

        return output

def sanitize(definition):
    def_text = re.sub("<strong>|</strong>","\x02", definition)
    def_text = re.sub("<br />|<br>"," ", def_text)
    def_text = re.sub("<.*?>"," ", def_text)
    def_text = re.sub("\s+"," ", def_text)
    l = def_text.splitlines()
    n = [item.strip() for item in l]
    def_text = " ".join(n).strip()
    def_text = formatting.truncate(def_text, 380)

    return def_text
