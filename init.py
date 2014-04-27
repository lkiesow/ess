from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
import sys
import subprocess, json

#############################################################################
## Database Schema Definition                                              ##
#############################################################################

Base = declarative_base()

class Artist(Base):
	__tablename__ = 'music_artist'

	id   = Column('id', Integer(unsigned=True), autoincrement='ignore_fk',
			primary_key=True)
	name = Column('name', String(255), nullable=False)

	def __repr__(self):
		return '<Artist(id=%i, name="%s")>' % (self.id, self.name)


class Album(Base):
	__tablename__ = 'music_album'

	id        = Column('id', Integer, autoincrement='ignore_fk',
			primary_key=True)
	name      = Column('name', String(255), nullable=False)
	artist_id = Column('artist_id', None, ForeignKey('music_artist.id'))

	artist = relationship("Artist", backref=backref('album', order_by=name))

	def __repr__(self):
		return '<Album(id=%i, name="%s", artist_id=%i)>' % \
				(self.id, self.name, self.artist_id)


class Song(Base):
	__tablename__ = 'music_song'

	id           = Column('id', Integer(unsigned=True), primary_key=True, autoincrement=True)
	title        = Column('name', String(255), nullable=False)
	year         = Column('year', Integer(unsigned=True))
	tracknumber  = Column('tracknumber', Integer(unsigned=True))
	times_played = Column('times_played', Integer(unsigned=True))
	uri          = Column('uri', String(2**16), nullable=False)
	genre        = Column('genre', String(255))
	artist_id    = Column('artist_id', None, ForeignKey('music_artist.id'))
	album_id     = Column('album_id', None, ForeignKey('music_album.id'))

	artist = relationship("Artist", backref=backref('song', order_by=title))
	album  = relationship("Album",  backref=backref('song', order_by=title))

	def __repr__(self):
		return '<Song(id=%i, title="%s", artist_id=%i)>' % \
			(self.id, self.title, self.artist_id)


#############################################################################
## Extract data from file                                                  ##
#############################################################################

def insert_song(uri):
	# TODO: Catch and handle errors
	stdout = subprocess.Popen( [ 'ffprobe', '-show_format', '-show_streams',
		'-of', 'json', uri ], stdout=subprocess.PIPE,
		stderr=subprocess.PIPE ).communicate()[0]
	data = json.loads(stdout)
	tags = data['format'].get('tags') or {}

	# Try to get the artist from db
	artist = None
	if tags.get('artist'):
		print '>>> Artist:', tags['artist']
		for a in session.query(Artist).filter(Artist.name==tags['artist']):
			artist = a
			break
		# Create new Artist if necessary
		if not artist:
			artist = Artist(name=tags['artist'])
			session.add(artist)

	# Try to get the album from db
	album = None
	if tags.get('album'):
		print '>>> Album:', tags['album']
		for a in session.query(Album).filter(Album.name==tags['album']).\
				filter(Album.artist==artist):
			album = a
			break
		# Create new album if necessary
		if not album:
			album = Album(name=tags['album'], artist=artist)
			session.add(album)

	song = Song(
			title=tags.get('title') or uri.rsplit('/',1)[-1],
			year=int(tags.get('date')),
			tracknumber=tags.get('track'),
			uri=uri,
			artist=artist,
			album=album
		)
	session.add(song)
	return song


#############################################################################
## Main program                                                            ##
#############################################################################

if __name__ == '__main__':
	#DATABASE = 'sqlite:///data.sqlite'
	DATABASE = 'mysql://ess:secret@localhost/ess'
	engine = create_engine(DATABASE, echo=True)
	Base.metadata.create_all(engine)
	Session = sessionmaker(bind=engine)
	session = None

	# Check if we want to insert test data as well
	if sys.argv[1:] == ['test']:
		session = Session()
		insert_song('http://storage-new.newjamendo.com/download/track/1093987/mp32')
		insert_song('http://storage-new.newjamendo.com/download/track/1107409/mp32')
		session.commit()
