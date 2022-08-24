#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Artist,Venue,Show
import phonenumbers

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.

#----------------------------------------------------------------------------#

#from models import *
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
  artists =Artist.query.order_by(Artist.created_at.desc()).limit(10).all()#Artist.query.all()
  #artists =Artist.query.order_by(Artist.id.desc()).limit(10).all() 
  venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()#.order_by(db.desc(Venue.created_at))
  return render_template('pages/home.html', artists =artists,venues=venues)

@app.route('/pages/home.html')
def home():
  artists =Artist.query.order_by(Artist.created_at.desc()).limit(10).all()
  venues = Venue.query.order_by(Venue.created_at.desc()).limit(10).all()
  return render_template('pages/home.html', artists =artists,venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  t =Show.query.join(Venue,Show.venue_id==Venue.id).filter(Show.starter_time > datetime.now() ).count()
  #return {str(1):'nebo'}
  s = Venue.query.all()
  #return {"city": s.city}

  
  a= []
  dic = {}
  for i in s:
    a.append(i.city)
    dic.update({
      str(i.city): i.state,
      #str(i.state): i.state,
    })
  b=set(a)
  l=list(b)
  #return dic
  d=[]
  for m in l:
    o={}
    dl= []
    t = Venue.query.filter_by(city=m).all()
    for din in t:
      tl =Show.query.join(Venue,Show.venue_id==Venue.id).filter(Show.venue_id == din.id ).filter(Show.starter_time > datetime.now() ).count()
      k={
        "id": din.id,
        "name": din.name,
        "num_upcoming_shows": tl,
      }
      dl.append(k)
    o['venues']  = dl
    o['city']  = m
    o['state']  = dic[str(m)]
    #o['state']
    d.append(o)
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  return render_template('pages/venues.html', areas=d);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term', '')
  venues = Venue.query.filter( Venue.name.ilike('%'+search+'%')).all()
  venues_count = Venue.query.filter( Venue.name.ilike('%'+search+'%')).count()
  my_response={}
  my_response['count']=venues_count
  my_response['data']=[]
  for venue in venues:
    u=0
    
    tt = Show.query.join(Venue,Show.artist_id==Venue.id).filter(Venue.id == venue.id).all()
    for i in tt:
      if datetime.now() <i.starter_time:
        u+=1
    my_response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": u,
    })
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=my_response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  t =Show.query.join(Venue,Show.venue_id==Venue.id).filter(Venue.id == venue_id ).all()

  venue = Venue.query.get(venue_id)
  mydata = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_venue": venue.seeking_venue,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows":[],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  
  past_shows = Show.query.join(Venue,Show.venue_id==Venue.id).filter(Venue.id == venue_id ).filter(Show.starter_time<datetime.now()).all()
  upcoming_shows = Show.query.join(Venue,Show.venue_id==Venue.id).filter(Venue.id == venue_id ).filter(Show.starter_time>datetime.now()).all()

  for i in past_shows:

    artist = Artist.query.get(i.artist_id)
    mydata["past_shows"].append({
      "artist_id":artist.id,
      "artist_name": artist.name,
      "artist_image_link":artist.image_link ,
      "start_time": str(i.starter_time)
      })
 
  for i in upcoming_shows:
    artist = Artist.query.get(i.artist_id)
    mydata["upcoming_shows"].append({
      "artist_id":artist.id,
      "artist_name": artist.name,
      "artist_image_link":artist.image_link ,
      "start_time": str(i.starter_time)
      })
  
  mydata['upcoming_shows_count']=Show.query.join(Venue,Show.venue_id==Venue.id).filter(Show.starter_time>datetime.now()).count()
  mydata['past_shows_count']=Show.query.join(Venue,Show.venue_id==Venue.id).filter(Show.starter_time<datetime.now()).count()
      

  
  # for i in t:
  #   artist = Artist.query.get(i.artist_id)
  #   if datetime.now() > i.starter_time:
  #     mydata['past_shows_count'] +=1
  #     mydata["past_shows"].append({
  #     "artist_id":artist.id,
  #     "artist_name": artist.name,
  #     "artist_image_link":artist.image_link ,
  #     "start_time": str(i.starter_time)

  #     })
  #   else:
  #     mydata['upcoming_shows_count'] +=1
  #     mydata["upcoming_shows"].append({
  #     "artist_id":artist.id,
  #     "artist_name": artist.name,
  #     "artist_image_link":artist.image_link ,
  #     "start_time": str(i.starter_time)

  #     })
  

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=mydata)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  form = VenueForm(request.form)
  error = False
  if form.validate(): #form.validate_on_submit():
    try:
      venue = Venue(name=form.name.data,city=form.city.data,state=form.state.data,
      address=form.address.data,phone=form.phone.data,genres =form.genres.data,
      image_link =form.image_link.data,facebook_link=form.facebook_link.data,
      website =form.website_link.data,seeking_venue=form.seeking_talent.data,
      seeking_description =form.seeking_description.data)
      db.session.add(venue)
      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  if error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  if not error:
    flash('An error occurred. Venue ' +request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
@app.route('/v', methods=['GET'])
def delete_v():
  venue = Artist.query.get(5)
  db.session.delete(venue)
  db.session.commit()
  error = False
  if error:
    return 'chidera'
  # venue = Venue.query.get(1)
  # db.session.delete(venue)
  # db.session.commit()
  return 'nebo'
  if request.get_json()['delete']:
    return jsonify({'success': True})




@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  if request.get_json()['delete']:
    try:

      #Venue.query.filter_by(id=venue_id).delete()
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
    except:

      db.session.rollback()
      return jsonify({'success': 'False'})
    finally:
      db.session.close()
      return jsonify({'success': 'True'})
    

  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #return None
  # return jsonify({'failure': True})
  # return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data1=[]
  for artist in artists:
    data1.append({
      "id": artist.id,
      "name": artist.name
    })
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  return render_template('pages/artists.html', artists=data1)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  
    
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term', '')
  artists = Artist.query.filter( Artist.name.ilike('%'+search+'%')).all()
  artists_count = Artist.query.filter( Artist.name.ilike('%'+search+'%')).count()
  my_response={}
  my_response['count']=artists_count
  my_response['data']=[]
  for artist in artists:
    u=0
    
    tt = Show.query.join(Artist,Show.artist_id==Artist.id).filter(Artist.id == artist.id ).all()
    for i in tt:
      if datetime.now() <i.starter_time:
        u+=1
    my_response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": u,
    })
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_artists.html', results=my_response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  t =Show.query.join(Artist,Show.artist_id==Artist.id).filter(Artist.id == artist_id ).all()
  artist = Artist.query.get(artist_id)
  mydata = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows":[],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  for i in t:
    venue = Venue.query.get(i.venue_id)
    if datetime.now() > i.starter_time:
      mydata['past_shows_count'] +=1
      mydata["past_shows"].append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(i.starter_time)

      })
    else:
      mydata['upcoming_shows_count'] +=1
      mydata["upcoming_shows"].append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": str(i.starter_time)

      })
  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=mydata)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
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
  # TODO: populate form with fields from artist with ID <artist_id>
  artist= Artist.query.get(artist_id)
  artist_dic = {
    
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  form = ArtistForm(data=artist_dic)
  form.website_link.data
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:

    form = ArtistForm(request.form)
    if form.validate(): #form.validate_on_submit():
      artist =Artist.query.get(artist_id)
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres =form.genres.data
      artist.image_link =form.image_link.data
      artist.facebook_link=form.facebook_link.data
      artist.website =form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description =form.seeking_description.data
      
      db.session.commit()
  except():
    db.session.rollback()
    
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
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
  # TODO: populate form with values from venue with ID <venue_id>
  venue= Venue.query.get(venue_id)
  venue_dic = {
    
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_venue,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  form = VenueForm(data=venue_dic)
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    form = VenueForm(request.form)
    if form.validate(): #form.validate_on_submit():
      venue = Venue.query.get(venue_id)
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.address=form.address.data
      venue.phone=form.phone.data
      venue.genres =form.genres.data
      venue.image_link =form.image_link.data
      venue.facebook_link=form.facebook_link.data
      venue.website =form.website_link.data
      venue.seeking_venue=form.seeking_talent.data
      venue.seeking_description =form.seeking_description.data
      
      db.session.commit()
  except():
    db.session.rollback()
    
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
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  form = ArtistForm(request.form)
  error = False
  def phone_format(n):
    return format(int(n[:-1]),',').replace(',','-')+n[-1]
  if form.validate(): #form.validate_on_submit():
    try:
      artist = Artist(name=form.name.data,city=form.city.data,state=form.state.data,
      phone=phone_format(form.phone.data),genres =form.genres.data,
      image_link =form.image_link.data,facebook_link=form.facebook_link.data,
      website =form.website_link.data,seeking_venue=form.seeking_venue.data,
      seeking_description =form.seeking_description.data)
      db.session.add(artist)
      db.session.commit()
    except():
      db.session.rollback()
      error = True
    finally:
      db.session.close()
    
    
   
    
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  if error:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  if not error:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  my_data = []
  for show in shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    k= {
      "venue_id": venue.id,
    "venue_name": venue.name,
    "artist_id":artist.id,
    "artist_name": artist.name,
    "artist_image_link": artist.image_link,
    "start_time":str(show.starter_time) #"2019-05-21T21:30:00.000Z"
    }
    my_data.append(k)
 
  return render_template('pages/shows.html', shows=my_data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error = False
  try:
    if form.validate(): #form.validate_on_submit():

      artist = Show(artist_id=form.artist_id.data,venue_id=form.venue_id.data,starter_time=form.start_time.data)
      db.session.add(artist)
      db.session.commit()
  except():
      db.session.rollback()
      error = True
  finally:
    db.session.close()
   

  # on successful db insert, flash success
  if error:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  if not error:
    flash('An error occurred. Show could not be listed.')
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
