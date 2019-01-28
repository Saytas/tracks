import xml.etree.ElementTree as ET
import sqlite3

connectionFile = sqlite3.connect("multiTableDatabaseTracks.sqlite")
cursorHandle = connectionFile.cursor()

### Make some fresh tables using executescript()
cursorHandle.executescript('''
	DROP TABLE IF EXISTS Artist;
	DROP TABLE IF EXISTS Genre;
	DROP TABLE IF EXISTS Album;
	DROP TABLE IF EXISTS Track;

	CREATE TABLE Artist (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
		name TEXT UNIQUE
	);

	CREATE TABLE Album (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
		artist_id INTEGER,
		title TEXT UNIQUE
	);

	CREATE TABLE Genre (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
		name TEXT UNIQUE
	);

	CREATE TABLE Track (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
		title TEXT UNIQUE,
		album_id INTEGER,
		genre_id INTEGER,
		len INTEGER, rating INTEGER, count INTEGER
	);
''')

fileName = input("Please enter the file name or enter 'quit': ")
##if fileName == "quit": break
if len(fileName) < 1: fileName = "Library.xml"

def lookup(d, key):
	found = False
	for child in d:
		if found: return child.text
		if child.tag == "key" and child.text == key:
			found = True
	return None

stuff = ET.parse(fileName)
##print(len(stuff))
allTracks = stuff.findall("dict/dict/dict")
print("Dict count:",len(allTracks))

for entry in allTracks:
	if lookup(entry, "Track ID") is None:
		continue
	name = lookup(entry,"Name")
	artist = lookup(entry,"Artist")
	album = lookup(entry,"Album")
	genre = lookup(entry,"Genre")
	count = lookup(entry,"Play Count")
	rating = lookup(entry,"Rating")
	length = lookup(entry,"Total Time")

	if name is None or artist is None or album is None or genre is None:
		continue

	print(name, artist, album, genre, count, rating, length)

	cursorHandle.execute("INSERT OR IGNORE INTO Artist (name) VALUES (?)",(artist,))
	## To know the primary key for the particular artist
	cursorHandle.execute("SELECT id FROM Artist WHERE name = ?",(artist,))
	artist_id = cursorHandle.fetchone()[0]

	cursorHandle.execute("INSERT OR IGNORE INTO Album (title,artist_id) VALUES (?,?)",(album,artist_id))
	## To know the primary key for the particular album
	cursorHandle.execute("SELECT id FROM Album WHERE title = ?",(album,))
	album_id = cursorHandle.fetchone()[0]

	cursorHandle.execute("INSERT OR IGNORE INTO Genre (name) VALUES (?)",(genre,))
	## To know the primary key for the particular genre
	cursorHandle.execute("SELECT id FROM Genre WHERE name = ?",(genre,))
	genre_id = cursorHandle.fetchone()[0]

	cursorHandle.execute('''INSERT OR REPLACE INTO Track (title,album_id,genre_id,len,rating,count) VALUES (?,?,?,?,?,?)''',
		(name,album_id,genre_id,length,rating,count))

	connectionFile.commit()

'''
SELECT Track.title, Artist.name, Album.title, Genre.name 
FROM Track JOIN Genre JOIN Album JOIN Artist 
ON Track.genre_id = Genre.ID and Track.album_id = Album.id 
AND Album.artist_id = Artist.id
ORDER BY Artist.name LIMIT 3
'''