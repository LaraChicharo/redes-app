import os
import json
import requests

KEY = os.environ['API_KEY']

BASE_URL = 'http://www.omdbapi.com/?apikey={}'.format(KEY)


def search_movie(title):
    url = '{}&s={}'.format(BASE_URL, title)
    res = requests.get(url)
    if res.status_code == 200:
        res = res.json()
        if res['Response']:
            return (200, res)
        else:
            return (404, None)
    else:
        return (res.status_code, None)
