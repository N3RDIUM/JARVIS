from googlesearch import search
import requests
from bs4 import BeautifulSoup

def search_google(dict_input):
    query = dict_input["query"]
    try:
        n = int(dict_input["n_results"])
    except KeyError:
        n = 16
    results = []
    for result in search(query, num_results=n, advanced=True):
        results.append({
            "url": result.url,
            "title": result.title,
            "description": result.description
        })
    return results
        
def search_weather(dict_input):
    location = dict_input["location"]
    
    # creating url and requests instance
    url = "https://www.google.com/search?q="+"weather"+location
    html = requests.get(url).content
    
    # getting raw data
    soup = BeautifulSoup(html, 'html.parser')
    temp = soup.find('div', attrs={'class': 'BNeawe iBp4i AP7Wnd'}).text
    str = soup.find('div', attrs={'class': 'BNeawe tAd8D AP7Wnd'}).text
    
    # formatting data
    data = str.split('\n')
    time = data[0]
    sky = data[1]
    
    # getting all div tag
    listdiv = soup.findAll('div', attrs={'class': 'BNeawe s3v9rd AP7Wnd'})
    strd = listdiv[5].text
    
    # getting other required data
    pos = strd.find('Wind')
    other_data = strd[pos:]
    return {
        "temperature": temp,
        "time": time,
        "sky": sky,
        "other_data": other_data
    }