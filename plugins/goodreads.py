from cloudbot import hook
from cloudbot.util import formatting
import urllib
import requests
from bs4 import BeautifulSoup

api_url = 'https://www.goodreads.com/search?utf8=%E2%9C%93&query={}'
base_url = 'https://www.goodreads.com{}'


@hook.command("goodreads", autohelp=False)
def goodreads(text):

    index = 0
    getindex = text.split(' ')
    if getindex[-1].isdigit():
        index = int(getindex[-1])-1
        title = ' '.join(getindex[:len(getindex)-1])
    else:
        title = text

    r = requests.get(api_url.format(urllib.parse.quote(title,safe='')))
    
    soup = BeautifulSoup(r.text,'html.parser')
    
    books = soup.find_all('tr',{'itemtype':'http://schema.org/Book'})
    
    results = len(books)
    
    if results == 0:
        return 'No results.'
    else:
        try:
            book_name = books[index].find_all('span',{'itemprop':'name'},limit=1)[0].text
            book_url = books[index].find_all('a',{'class':'bookTitle','itemprop':'url'})[0]['href']
            book_url = base_url.format(book_url)
            shortened = requests.get('https://is.gd/create.php?format=simple&url={}'.format(book_url)).text
            book_author = books[index].find_all('a',{'class':'authorName'})[0].text
            ratings = books[index].find_all('span',{'class':'minirating'})[0].text.strip()
            return '[{}/{}] {} - by {} ({}) : {}'.format(index+1,results, book_name, book_author, ratings, shortened)
        except IndexError:
            return 'No results.'
