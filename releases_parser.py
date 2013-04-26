#!/usr/bin/python
from pymongo import Connection
from lxml import etree

# Asetukset

releasesxml = 'discogs_20130301_releases.xml'
connection = Connection('localhost',27017)
db = connection.discogs
releases = db.releases

file = open(releasesxml,'r')

events = ("start", "end")
context = etree.iterparse(file, events=events)
event, root = context.next()
i = 1

# Releaselta halutut tiedot
Release = {'release_id':None,\
           'artist':'',\
           'release':'',\
           'tracklist':[],\
           'imageurl':'',\
           'thumbnail':'',\
           'genre':[],\
           'style':[],\
           'format':'',\
           'country':'',\
           'labels':[],\
           'released':{'year':0,'month':0,'day':0},\
           'videos':[]}

# Luetaan XML-tiedostosta elementti kerrallaan
for action, elem in context:

 # Kun kohdalla 'release' elementin loppu (action == 'end') ja release on hyväksytty, käsitellaan sen tiedot
 if elem.tag == 'release' and action == 'end' and len(elem.getchildren()) > 5 and elem.values()[1] == 'Accepted':

   store = Release.copy()
   store['release_id'] = int(elem.values()[0])
   store['artist'] = elem.xpath('./artists/artist/name')[0].text
   store['release'] = elem.xpath('./title')[0].text
   if len(elem.xpath('./released')) > 0:
       release_date = elem.xpath('./released')[0].text.split('-')
       store['released']['year']=release_date[0]

   if len(elem.xpath('./images/*')) > 0:
      store['imageurl'] = elem.xpath('./images/*/@uri')[0]
      store['thumbnail'] = elem.xpath('./images/*/@uri150')[0]

   store['genre'],store['style'],store['tracklist'],store['videos'],store['labels']=[],[],[],[],[]
   for genre in elem.xpath('./genres/*'): store['genre'].append(genre.text)
   for style in elem.xpath('./styles/*'): store['style'].append(style.text)

   for track in elem.xpath('./tracklist/track'):
      store['tracklist'].append({'Position':track.xpath('./position')[0].text,'Title':track.xpath('./title')[0].text,'Duration':track.xpath('./duration')[0].text})

   if len(elem.xpath('./labels/*')) > 0:
      for label in elem.xpath('./labels/*'): store['labels'].append(label.values()[1])

   for video in elem.xpath('./videos/*'):
       store['videos'].append({ \
                               'URL':video.xpath('./@src'),\
                               'Description':video.xpath('./description')[0].text,\
                               'Title':video.xpath('./title')[0].text\
                              })
   elem.clear()
   root.clear()
   releases.insert(store)

   # Tulostetaan 500 kpl valein tallennettu määrä konsoliin
   if i%500==0:
    print str(i) + 'kpl tallennettu.'
   i += 1

