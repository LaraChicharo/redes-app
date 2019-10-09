import os
import json
import requests

KEY = os.environ['API_KEY']

BASE_URL = 'http://www.omdbapi.com/?apikey={}'.format(KEY)


def search_movie(title):
    url = '{}&t={}'.format(BASE_URL, title)
    r = requests.get(url)
    if r.status_code == 200:
        r = r.json()
        title = r.get('Title')
        return (200, title)
    else:
        print('error: ')
        print(r.text)
        return (r.status_code, None)
