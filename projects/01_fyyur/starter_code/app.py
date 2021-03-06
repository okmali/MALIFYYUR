#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
#SQLALCHEMY_DATABASE_URI and SQLALCHEMY_TRACK_MODIFICATIONS attributes are set in config

migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres=db.Column(db.String(120))
    website=db.Column(db.String(120))
    facebook_link=db.Column(db.String(120))
    seeking_talent=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(120))
    venueshow=db.relationship('Shows', backref='venueshow',lazy=True)
    #-----------------------------------------------


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website=db.Column(db.String(120))
    seeking_venue=db.Column(db.Boolean)
    seeking_description=db.Column(db.String(120))
    #-------------------------------------------------
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
    artistshow=db.relationship('Shows', backref='artistshow',lazy=True)


#Shows is association table
class Shows(db.Model):
    __tablename__='shows'

    id=db.Column(db.Integer, primary_key=True)
    artist_id=db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
    venue_id=db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
    startdate=db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  venuecities=db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  data= []
  i=0
  for venuecity in venuecities:
    newNode={}
    newNode['city']=venuecities[i].city
    newNode['state']=venuecities[i].state
    venues=db.session.query(Venue.id,Venue.name).filter(Venue.city==venuecity.city).all()
    
    m=0
    venueNodeBody=[]
    for venue in venues:
      venueNode={}
      venueNode['id']=venue.id
      venueNode['name']=venue.name
      #count=db.session.query(db.func.count(Shows.artist_id)).filter_by(Shows.startdate > datetime.now(),  Shows.venue_id==venue.id).all()
      count=db.session.query(Shows.artist_id).filter(Shows.startdate > datetime.now()).filter(Shows.venue_id==venue.id).count()
      print(count)
      venueNode['num_upcoming_shows']=count
      venueNodeBody.append(venueNode)
      m+=1
    newNode['venues'] =venueNodeBody
    data.append(newNode)
    i+=1
#------------------------------------------------

  #data=[{
  #  "city": "San Francisco",
  #  "state": "CA",
  #  "venues": [{
  #    "id": 1,
  #    "name": "The Musical Hop",
  #    "num_upcoming_shows": 0,
  #  }, {
  #    "id": 3,
  #    "name": "Park Square Live Music & Coffee",
  #    "num_upcoming_shows": 1,
  #  }]
  #}, {
  #  "city": "New York",
  #  "state": "NY",
  #  "venues": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}]
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  #req = request.get_json()
  search_term=request.form.get('search_term', '')
  
  q = "%{}%".format(search_term)
  venues=db.session.query(Venue).filter(Venue.name.ilike(q)).all()
  countofsearchitems=len(venues)

  data= {}
  data['count']= countofsearchitems

  i=0
  dataNode=[]
  for venue in venues:
    dataNodeElement={}
    venueid=venue.id
    num_of_upcoming_shows=db.session.query(Shows.venue_id).filter(Shows.startdate > datetime.now()).filter(Shows.venue_id==venue.id).count()
    dataNodeElement['id']=venues[i].id
    dataNodeElement['name']=venues[i].name
    dataNodeElement['num_upcoming_shows']=num_of_upcoming_shows
    dataNode.append(dataNodeElement)
    i+=1

  data['data']= dataNode
 
  #response={
  #  "count": 1,
  #  "data": [{
  #    "id": 2,
  #    "name": "The Dueling Pianos Bar",
  #    "num_upcoming_shows": 0,
  #  }]
  #}
  #return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
  return render_template('pages/search_venues.html', results=data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue=db.session.query(Venue).filter(Venue.id==venue_id).one()
  genres=[]
  genres=venue.genres.split(',')

  data={}
  data['id']=venue.id
  data['name']=venue.name
  data['genres']=genres
  data['address']=venue.address
  data['city']=venue.city
  data['state']=venue.state
  data['phone']=venue.phone
  data['website']=venue.website
  data['facebook_link']=venue.facebook_link
  data['seeking_talent']=venue.seeking_talent
  data['seeking_description']=venue.seeking_description
  data['image_link']=venue.image_link
  
  showsandartists=db.session.query(Shows,Artist).join(Artist).filter(Shows.venue_id==venue_id).all()
  
  pastShowNode=[]
  upcomingShows=[]
  i=0
  pastShowCount=0
  upcomingShowCount=0
  for showsandartist in showsandartists:
    showdate=showsandartist[0].startdate
    upcomingshow={}
    pastshow={}
    if showdate > datetime.now():
      upcomingshow['artist_id']=showsandartist[1].id
      upcomingshow['artist_name']=showsandartist[1].name
      upcomingshow['artist_image_link']=showsandartist[1].image_link
      upcomingshow['start_time']=showsandartist[0].startdate.strftime("%m/%d/%Y %H:%M:%S")
      upcomingShows.append(upcomingshow)
      upcomingShowCount+=1
    else:
      pastshow['artist_id']=showsandartist[1].id
      pastshow['artist_name']=showsandartist[1].name
      pastshow['artist_image_link']=showsandartist[1].image_link
      pastshow['start_time']=showsandartist[0].startdate.strftime("%m/%d/%Y %H:%M:%S")
      pastShowNode.append(pastshow)
      pastShowCount+=1

  data['past_shows']=pastShowNode
  data['upcoming_shows']=upcomingShows
  data['past_shows_count']= pastShowCount
  data['upcoming_shows_count']= upcomingShowCount
  
  return render_template('pages/show_venue.html', venue=data)
  

"""   data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
     "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  } 

  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0] """
  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  newVenue=Venue()

  newVenue.name=request.form.get('name','')
  
  newVenue.genres=getGenresStr(request.form.getlist('genres'))
  newVenue.city=request.form.get('city','')
  newVenue.state=request.form.get('state','')
  newVenue.address=request.form.get('address','')
  newVenue.phone=request.form.get('phone','')
  newVenue.website=request.form.get('website_link','')
  newVenue.facebook_link=request.form.get('facebook_link','')
  newVenue.seeking_talent=(False, True)[request.form.get('seeking_talent','').lower() =='y']
  newVenue.seeking_description=request.form.get('seeking_description','')
  newVenue.image_link=request.form.get('image_link','')
  
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  try:
    db.session.add(newVenue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Artist ' +  request.form['name'] + ' could not be listed!')
  finally:  
    db.session.close() 

  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #venue=Venue()
  #venue=db.session.query(Venue).get(venue_id)
  try:
    db.session.query(Venue).filter(Venue.id==venue_id).delete()
    db.commit()
    flash('Venue ' + request.form['name'] + ' was successfully deleted!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Venuw ' +  request.form['name'] + ' could not be deleted!')
  finally:  
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artistList=db.session.query(Artist.id,Artist.name).all()
  return render_template('pages/artists.html', artists=artistList)

"""   data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }] """
  #return render_template('pages/artists.html', artists=data)
  

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  q = "%{}%".format(search_term)
  artistList=db.session.query(Artist).filter(Artist.name.ilike(q)).all()
  countofartistitems=len(artistList)

  data= {}
  data['count']= countofartistitems

  dataNode=[]
  i=0
  for artist in artistList:
    d={}
    d['id']=artist.id
    d['name']=artist.name
    num_of_upcoming_shows=db.session.query(Shows).filter(Shows.startdate > datetime.now()).filter(Shows.artist_id==artist.id).count()
    d['num_upcoming_shows']=num_of_upcoming_shows
    dataNode.append(d)
    i+=1
  data['data'] = dataNode 
  return render_template('pages/search_artists.html', results=data, search_term=request.form.get('search_term', ''))

"""   response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  } """
  #return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=db.session.query(Artist).filter(Artist.id==artist_id).one()
  genres=[]
  genres=artist.genres.split(',')

  data={}
  data['id']=artist.id
  data['name']=artist.name
  data['genres']=genres
  data['city']=artist.city
  data['state']=artist.state
  data['phone']=artist.phone
  data['website']=artist.website
  data['facebook_link']=artist.facebook_link
  data['seeking_venue']=artist.seeking_venue
  data['seeking_description']=artist.seeking_description
  data['image_link']=artist.image_link
  
  #showsandartists=db.session.query(Shows,Artist).join(Artist).filter(Shows.artist_id==artist_id).all()
  showsandartists=db.session.query(Shows,Artist,Venue).join(Artist).join(Venue).filter(Shows.artist_id==artist_id,Shows.venue_id==Venue.id).all()
  
  pastShowNode=[]
  upcomingShows=[]
  i=0
  pastShowCount=0
  upcomingShowCount=0
  for showsandartist in showsandartists:
    showdate=showsandartist[0].startdate
    upcomingshow={}
    pastshow={}
    if showdate > datetime.now():
      upcomingshow['venue_id']=showsandartist[2].id
      upcomingshow['venue_name']=showsandartist[2].name
      upcomingshow['venue_image_link']=showsandartist[2].image_link
      upcomingshow['start_time']=showsandartist[0].startdate.strftime("%m/%d/%Y %H:%M:%S")
      upcomingShows.append(upcomingshow)
      upcomingShowCount+=1
    else:
      pastshow['venue_id']=showsandartist[2].id
      pastshow['venue_name']=showsandartist[2].name
      pastshow['venue_image_link']=showsandartist[2].image_link
      pastshow['start_time']=showsandartist[0].startdate.strftime("%m/%d/%Y %H:%M:%S")
      pastShowNode.append(pastshow)
      pastShowCount+=1

  data['past_shows']=pastShowNode
  data['upcoming_shows']=upcomingShows
  data['past_shows_count']= pastShowCount
  data['upcoming_shows_count']= upcomingShowCount

  return render_template('pages/show_artist.html', artist=data)

"""   data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  } """
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=db.session.query(Artist).filter(Artist.id==artist_id).one()
  return render_template('forms/edit_artist.html', form=form, artist=artist)
"""  
 artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  } 
  """
  # TODO: populate form with fields from artist with ID <artist_id>
  #return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist()
  artist=db.session.query(Artist).get(artist_id)
  artist.name=request.form.get('name','')
  artist.genres=getGenresStr(request.form.getlist('genres'))
  artist.city=request.form.get('city','')
  artist.state=request.form.get('state','')
  artist.phone=request.form.get('phone','')
  artist.website=request.form.get('website','')
  artist.facebook_link=request.form.get('facebook_link','')
  artist.seeking_venue=(False, True)[request.form.get('seeking_venue','').lower() =='y']
  artist.seeking_description=request.form.get('seeking_description','')
  artist.image_link=request.form.get('image_link','')
  
  try:
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Artist ' +  request.form['name'] + ' could not be updated!')
  finally:  
    db.session.close() 
  
  
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=db.session.query(Venue).filter(Venue.id==venue_id).one()
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  """
   venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  } 
  """
  # TODO: populate form with values from venue with ID <venue_id>
  #return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue=Venue()
  venue=db.session.query(Venue).get(venue_id)
  venue.name=request.form.get('name','')
  venue.genres=getGenresStr(request.form.getlist('genres'))
  venue.city=request.form.get('city','')
  venue.state=request.form.get('state','')
  venue.address=request.form.get('address','')
  venue.phone=request.form.get('phone','')
  venue.website=request.form.get('website_link','')
  venue.facebook_link=request.form.get('facebook_link','')
  venue.seeking_talent=(False, True)[request.form.get('seeking_talent','').lower() =='y']
  venue.seeking_description=request.form.get('seeking_description','')
  venue.image_link=request.form.get('image_link','')
  
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  try:
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Artist ' +  request.form['name'] + ' could not be updated!')
  finally:  
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  newArtist=Artist()

  newArtist.name=request.form.get('name','')
  newArtist.genres=getGenresStr(request.form.getlist('genres'))
  newArtist.city=request.form.get('city','')
  newArtist.state=request.form.get('state','')
  newArtist.phone=request.form.get('phone','')
  newArtist.website=request.form.get('website','')
  newArtist.facebook_link=request.form.get('facebook_link','')
  newArtist.seeking_venue=(False, True)[request.form.get('seeking_venue','').lower() =='y']
  newArtist.seeking_description=request.form.get('seeking_description','')
  newArtist.image_link=request.form.get('image_link','')
  
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  try:
    db.session.add(newArtist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    print(sys.exc_info)
    db.session.rollback()
    flash('An error occurred. Artist ' +  request.form['name'] + ' could not be listed.')
  finally:  
    db.session.close() 

    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  showList=db.session.query(Shows.startdate,Venue.id,Venue.name,Artist.id,Artist.name,Artist.image_link).join(Artist).join(Venue).all()
  
  i=0
  data=[]
  
  for show in showList:
    
    showRec={}
    showRec['venue_id']=show[1]
    showRec['venue_name']=show[2]
    showRec['artist_id']=show[3]
    showRec['artist_name']=show[4]
    showRec['artist_image_link']=show[5]
    showRec['start_time']=show[0].strftime("%m/%d/%Y %H:%M:%S")
    data.append(showRec)
    i+=1

  #print('Data len:',len(data))
  #print(data)
  return render_template('pages/shows.html', shows=data)
  ''' 
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)
'''

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id=request.form.get('artist_id','')
  venue_id=request.form.get('venue_id','')
  startdate=request.form.get('start_time','')
  print('reqData:',artist_id,' ',venue_id,' ',startdate)
  show=Shows()
  show.artist_id=artist_id
  show.venue_id=venue_id
  show.startdate=datetime.strptime(startdate,("%Y-%m-%d %H:%M:%S"))
 
  # on successful db insert, flash success
  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed!')
  finally:  
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

def getGenresStr (genresList):
  retVal=''
  rangeVal=len(genresList)
  for i in range(0, rangeVal):
    retVal=retVal+genresList[i]
    if i< rangeVal-1:
      retVal=retVal+","
  return retVal
    


#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
