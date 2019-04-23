import requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from cloudbot import hook

# Returns a list of dictionaries
def get_results(game_name, index = 0):
    base_url = 'https://howlongtobeat.com/search_results.php?page=1'
    post_data = {'queryString':'','sorthead':'popular'}

    post_data['queryString'] = game_name

    r = requests.post(base_url, data = post_data)

    soup = BeautifulSoup(r.text, 'html.parser')

    games = soup.findAll('li', {'class', 'back_darkish'})

    results = []

    for item in games:
      game = {}
      gamedata = {}
      game['title'] = item.h3.a['title']
      game['href'] = item.h3.a['href']
      
      info_description = item.findAll('div', {'class': 'search_list_tidbit', 'class': 'text_white'})
      info_value = item.findAll('div', {'class': 'search_list_tidbit', 'class': 'center'})

      for i in range(0, len(info_description)):
        gamedata[info_description[i].text] = info_value[i].text.strip()

      # A subdictionary with the completion time data. Doesn't always comes in 3 pairs
      game['data'] = gamedata
      
      results.append(game)

    return results


@hook.command("howlongtobeat", "hltb", autohelp=False)
def howlongtobeat(text):
    """<game title> [, index] - Returns the game entry from howlongtobeat.com"""

    if text:
        # clean and split the input
        text = text.lower().strip()
        splitted = text.split(',')
        
        game_title = splitted[0].strip()
        
        # get index, if available
        if len(splitted) > 1 and splitted[1].strip().isdigit():
            index = abs(int(splitted[1]))
        else:
            index = 1

        # fetch results
        results = get_results(game_title)
        
        if not results:
            return 'No results for \'{}\''.format(game_title)

        # if invalid index, show last result
        if len(results) < index:
            index = len(results)
            
        g = results[index - 1]
        
        output = '[{}/{}] [{}]'.format(index, len(results), g['title'])
        
        for key, value in g['data'].items():
          output += ' ({}: {}) '.format(key, value)

        output += requests.get('https://is.gd/create.php?format=simple&url={}'.format('https://howlongtobeat.com/' + g['href'])).text

        return output
    else:
        return 'Usage: <game title> [, id]'
