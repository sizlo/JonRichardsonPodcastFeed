import json
import re
import PyRSS2Gen
import datetime

def getIndexFromTitle(title):
    indexString = ''
    for c in title:
        if not c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            break
        indexString += c
    return int(indexString)

def correctIndex(index):
    if index >= 60:
        correctedIndex = index - 59
    else:
        correctedIndex = index + 87
    return correctedIndex

with open('JonRichardsonPodcast.json') as dataFile:
    data = json.load(dataFile)

correctedEpisodes = [None] * 146

for episode in data:
    title = episode['title']
    index = getIndexFromTitle(title)

    # archive.org has the files in the wrong order
    correctedIndex = correctIndex(index)
    correctedTitle = title.replace(str(index), str(correctedIndex), 1)

    date = re.search('\d{4}-\d{2}-\d{2}', title).group(0)

    for source in episode['sources']:
        if source['type'] == 'mp3':
            mp3Link = source['file']
        if source['type'] == 'ogg':
            oggLink = source['file']

    correctedEpisode = {}
    correctedEpisode['title'] = correctedTitle
    correctedEpisode['mp3'] = mp3Link
    correctedEpisode['ogg'] = oggLink
    correctedEpisode['date'] = date

    correctedEpisodes[correctedIndex-1] = correctedEpisode

rssEpsiodes = []
for episode in reversed(correctedEpisodes):
    dateElements = episode['date'].split('-')
    date = datetime.datetime(int(dateElements[0]), int(dateElements[1]), int(dateElements[2]))

    rssEpisode = PyRSS2Gen.RSSItem(
        title = episode['title'],
        pubDate = date,
        # PyRSS2Gen doesn't seem to support enclosures, so use the 
        # guid tag which we can hack around after writing the xml
        guid = 'https://archive.org' + episode['mp3']
    )
    rssEpsiodes.append(rssEpisode)

rss = PyRSS2Gen.RSS2(
    title = 'Jon Richardson Podcasts',
    link = 'https://archive.org/details/JonRichardsonPodcast',
    description = 'Jon Richardsons BBC 6 Music radio shows. Hosted by https://archive.org. RSS feed by Tim Brier.',
    lastBuildDate = datetime.datetime.now(),
    items = rssEpsiodes
)

rss.write_xml(open('JonRichardsonPodcast.xml', 'w'))

with open('JonRichardsonPodcast.xml') as xmlFile:
    xmlContents = xmlFile.read()
xmlContents = xmlContents.replace('<guid>', '<enclosure url="')
xmlContents = xmlContents.replace('</guid>', '" type="audio/mp3" />')
with open('JonRichardsonPodcast.xml', 'w') as xmlFile:
    xmlFile.write(xmlContents)