import os
import json
import requests

KEY = os.environ['API_KEY']

BASE_URL = 'http://www.omdbapi.com/?apikey={}'.format(KEY)


def search_movie(title):
    url = '{}&s={}'.format(BASE_URL, title)
    res = requests.get(url)
    resd = res.json()
    if resd['Response'] == 'True':
        return (200, True, resd)
    else:
        return (res.status_code, False, resd['Error'])


def search_movie_id(imdbid):
    url = '{}&i={}'.format(BASE_URL, imdbid)
    res = requests.get(url)
    resd = res.json()
    if resd['Response'] == 'True':
        return (200, True, resd)
    else:
        return (res.status_code, False, resd.get('Error'))
