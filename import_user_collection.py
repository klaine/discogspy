#!/usr/bin/python
import json
import urllib2
import datetime
import collections
from pymongo import MongoClient

# Discogs tunnus
discogs_user = 'jell-o'

# MongoDB asetukset
client = MongoClient()
db= client.discogs
records = db.releases
catalogs = db.catalogs

# Muut asetukset
page = 1
data,releases = [],[]
discogs_url = 'http://api.discogs.com/users/'+discogs_user+'/collection/folders/0/releases?per_page=100'

# Timestamp stringina
def ts():
   return str(datetime.datetime.utcnow())

# Jos käyttäjän kokoelmaa ei löydy kannasta
if catalogs.find_one({'discogs_user':discogs_user}) == None:
    # Ladataan 1. sivu ja katsotaan montako sivua loytyy lisaa
    data.append(json.loads(urllib2.urlopen(discogs_url).read()))
    pages = data[0]['pagination']['pages']

    # Haetaan loput sivut
    print ts() + '\tLoading Discogs.com user collection for user: %s' % discogs_user
    while page < pages:
        data.append(json.loads(urllib2.urlopen(data[page-1]['pagination']['urls']['next'].encode('ascii')).read()))
        page += 1
        print ts() + '\tPage %d loaded...' % page

    # Haetaan ladatuista tiedoista levyjen release_id tiedot taulukkoon
    print ts() + '\tGetting release ID\'s from %s\'s fetched data..' % discogs_user
    for page in data:
        for release in page['releases']:
            releases.append(release['id'])
    print ts() + '\tFound %d releases!' % len(releases)
    print ts() + '\tInserting release_id values to database'

    # Tallennetaan collections kokoelmaan kantaan tunnus, hakupvm ja release_id:t
    catalogs.insert({'discogs_user':discogs_user,'releases':releases,'updated':ts()})
    print ts() + '\tCollection saved into database!'

# Jos käyttäjätunnuksen kokoelma on jo kannassa:
else:
    print ts() + '\tUser %s has already imported a catalog' % discogs_user
