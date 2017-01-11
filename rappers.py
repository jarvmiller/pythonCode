# compare 'mumble rappers' to the (imo) top rappers ie kendrick, jcole, etc.

from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.parse import urlparse
import urllib.parse
from adjustText import adjust_text


"""
Function
--------
rapperDriver

calls all necessary functions to get each song url,
get len(unique lyrics), get song duration,
create df, and plot if desired

Parameters
-----------
artist : string
    Desired artist
album : string
    Desired album
toPlot : boolean
	If you want to plot song duration vs len(unique lyrics). Default = True

Returns
--------
df : A Pandas dataframe
  

Examples
---------
>>> print win_percentage('Kendrick Lamar', "To pimp a butterfly")
"""


def rapperDriver(artist, album, toPlot=True):
	artist, album = str(artist), str(album)  # just in case
	song_links = getSongLinks(artist, album)
	df = uniqueLyrics(song_links)
	df['artist'] = artist  # add artist label
	df['length'] = songLen(artist, album, len(song_links) + 1)
	df['trackNum'] = (df.index + 1)

	if toPlot:
		ax = sns.regplot(x=df.length, y=df.nLyrics, fit_reg=False, data=df)
		ax.set(xlabel='song length (seconds)', ylabel='num unique words', title = artist + '-' + album)
		texts = []
		for xt, yt, s in zip(df.length, df.nLyrics, df.Song):  
		# plt.text(x_coord, y_coord, label to put on that coord)
			texts.append(plt.text(xt, yt, s))
		adjust_text(texts, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))

		plt.show()

	return df

"""
Function
--------
getSongLinks

scrapes genius.com to get the url for each song in the specified album.

Parameters
-----------
artist : string
    Desired artist
album : string
    Desired album

Returns
--------
song_links : A list of urls

Examples
---------
>>> print getSongLinks('Kendrick Lamar', "To pimp a butterfly")
"""


def getSongLinks(artist, album):
	artist, album = str(artist), str(album)

	artist = artist.replace('.', '')
	artist = re.sub(' ', '-', artist)
	album = album.replace('.', '')
	album = re.sub(' ', '-', album)

	url = "http://genius.com/albums/" + str(artist) + '/' + str(album)

	req = requests.get(url)
	page = req.text
	soup = BeautifulSoup(page, 'html.parser')

	# ul has track titles in order
	song_ul = soup.find("ul", {"class" : "song_list primary_list has_track_order"})
	song_links = [l.get('href') for l in song_ul.findAll('a')[0:albumLen(soup)]]

	return song_links


# but first, be sure that you're only getting the track numbers..

"""
Function
--------
albumLen

Takes the soup object for the specified album's webpage 
and counts the number of album tracks
that have a track number

Parameters
-----------
soup : BeautifulSoup object


Returns
--------
counter : A natural number


Examples
---------
>>> albumLen(soup)
"""
def albumLen(soup, counter=0):

# hasNumbers takes the text under the 'track number' class and sees whether it is a number or a '?'
	def hasNumbers(inputString):
		return any(char.isdigit() for char in inputString)

	# Span -> class 'track_number' is either a number or a question mark
	for link in soup.findAll("span", {"class": "track_number"}):
		if hasNumbers(link.text):  # If we have a numbered track
			counter += 1
	return counter

"""
Function
--------
uniqueLyrics

accepts a song url[s] (list) from the getSongLinks function.
Returns dataframe with columns that refer to the song 
title and number of unique lyrics.

Parameters
-----------
soup_url : list


Returns
--------
df : A Pandas dataframe
    

Examples
---------
>>> uniqueLyrics(getSongLinks(artist, album))
"""


def uniqueLyrics(song_url):

	li_title = []
	li_lyrics = []

	for song in song_url:
		req = requests.get(song).text
		soup = BeautifulSoup(req, 'html.parser')

		# getting the song title
		x = soup.title.text.split(' ')

		# this assumes x has form [artist_name, -, song title..., Lyrics]
		title = ' '.join(x[2 : x.index("Lyrics")]) 
		li_title.append(title)

		allLyrics = [l.text for l in soup.findAll('p') if '\n' in l.text]
		song_lyrics = ''.join(allLyrics)

		# get rid of square brackets and anything between them ie [hook], [verse i], etc
		song_lyrics = re.sub('\[.*\]', '', song_lyrics) 

		# get rid of all special characters except spaces
		song_lyrics = re.sub('[^a-zA-Z0-9 \n\.]', '', song_lyrics)

		song_lyrics = song_lyrics.lower()

		# get rid of the 'new line' elts.. not removed from the previous re.sub for some reason..
		song_lyrics = re.sub('[\n]', ' ', song_lyrics)

		# subtract one because of the ' ' in the set after replacing \n w/ ' '
		tot_lyrics = len(set(song_lyrics.split(' '))) - 1
		li_lyrics.append(tot_lyrics)

	df = pd.DataFrame({"Song": li_title, "nLyrics": li_lyrics})
	return df


"""
Function
--------
songLen

For a specified artist and album, this funtion attempts to scrape a wikipedia table containing each
song's duration. This is not robust yet because most wiki tables have varying format or the information 
is in a list instead.

Parameters
-----------
artist : string
    Desired artist
album : string
    Desired album
length : positive integer

Returns
--------
duration : A list
    

Examples
---------
>>> uniqueLyrics('kendrick lamar', 'to pimp a butterfly', len(song_list))
"""


def songLen(artist, album, length):
	artist, album = artist.replace(' ', '+'), album.replace(' ', '+')

	url = 'https://www.google.com/search?q=' + artist + '+' + album + '+wiki'
	req = requests.get(url)

	soup = BeautifulSoup(req.text, 'lxml')

	# gotta do this hella weird thing to get the url. see - http://stackoverflow.com/questions/21934004/not-getting-proper-links-from-google-search-results-using-mechanize-and-beautifu
	for a in soup.select('.r a'):
		if 'en.wikipedia.org' in urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)['q'][0]:
			url = urllib.parse.parse_qs(urllib.parse.urlparse(a['href']).query)['q'][0]
			break

	req = requests.get(url)
	soup = BeautifulSoup(req.text, 'lxml')

	tab = soup.find('table', {"class" : 'tracklist'}) 
	duration = []
	for row in tab.findAll('tr')[1:length]:
		col = row.findAll('td')[-1].text
		m, s = col.split(":")
		duration.append(int(m)*60 + int(s))

	return duration


rapperDriver('kendrick lamar', 'to pimp a butterfly')
rapperDriver('J. cole', '4 your eyez only')
rapperDriver('Anderson .paak', 'malibu')
rapperDriver('desiigner', 'new english')
rapperDriver('lil uzi vert', '1017 vs the world')
rapperDriver('2pac', 'me against the world')

# to do - get song title in songLen function and merge based on that.. indices for songs dont match up at times
# between genius and wikipedia ie 'slaughter your daughter' is song 14 on genius, song 5 on wiki
# but at the same time.. one song has the 'liq' in the title on genius and 'lick' on wikipedia