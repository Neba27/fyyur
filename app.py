#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import collections
collections.Callable = collections.abc.Callable
from datetime import datetime

# import Models
from models import db, Artist, Venue, Shows

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config.from_object('config') # db URI from the config.py file
migrate = Migrate(app, db)       # database migration using Flask-Migrate

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Models have been moved to models.py as per the instruction .

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
  venues = Venue.query.all()          
  data = []                           
  list_city = []                      
  list_shows = []                     
  for venue in venues:                
    list_city.append((venue.city, venue.state))
    for city in list_city:
      if (venue.city == city[0]) and (venue.state == city[1]): 
        shows_list = list(filter(lambda s : s.start_time > datetime.now(), venue.show))
        list_shows.append({          
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(shows_list) 
        })
        dict_citystate = { "city" : venue.city, "state" : venue.state } 
        dict_citystate["venues"] = list_shows
        data.append(dict_citystate)         

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  venues_search = request.form.get("search_term", "")
  response = {}     
  venues_search = Venue.query.filter(Venue.name.ilike(f"${venues_search}$")).all()
  for venue in venues_search:
    list_shows = list(filter(lambda s: s.start_time > datetime.now(), venue.shows))
    ven_shows = {
      "id": venue.id,
      "name": venue.name,       
      "num_upcoming_shows": len(list_shows)
    }
    response["count"] = len(venues_search) # Add the number of results to the response dict
    response["data"] = []          
    response["data"].append(ven_shows)
  return render_template('pages/search_venues.html', results=response, search_term=venues_search)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)     # Obtain the data for that venue_id
  # Store all the past shows to a var past_shows
  past_shows = list(filter(lambda p: p.start_time < datetime.now(), venue.show))
  # Store all the upcoming shows to a var upcoming_shows
  upcoming_shows = list(filter(lambda u: u.start_time >= datetime.now(), venue.show))

  ven_dict = {
        **venue.__dict__,         # Build a dictionary on the original venue varieble
        **{                       
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),            
            'upcoming_shows_count': len(upcoming_shows)            
        }}

  return render_template('pages/show_venue.html', venue=ven_dict)

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
  form = VenueForm(request.form)

  if form.validate():             
    try:
      new_venue = Venue(          
        name=form.name.data,      
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        genres=",".join(form.genres.data),    
        facebook_link=form.facebook_link.data,
        image_link=form.image_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data,
        website_link=form.website_link.data,
      )
      db.session.add(new_venue)         
      db.session.commit()
    # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except Exception:
      db.session.rollback()
      flash('An error occured. Venue ' + request.form['name'] + ' could not be listed.')
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.close()
  else:
    flash("Venue was not listed!")

    # return render_template('pages/home.html')
  return redirect(url_for('venues'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail. 
  venue = Venue.query.get(venue_id)           # Obtain data based on id
  if venue:
    try:
      venue_name = venue.name         
      db.session.delete(venue_name)   
      db.session.commit()             
      flash("Selected Venue: " + venue_name + " has been deleted succesfully.")
    except:
      db.session.rollback()
    finally:
      db.session.close()
  else:
    return redirect(url_for('venues'))
  

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  
  artists = db.session.query(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response = {}
  artist_search = request.form.get('search_term', '')
  # Query all the artists based on the input
  # Store these results in a variable
  artists = Artist.query.filter(Artist.name.ilike(f"${artist_search}$")).all()                               
  response["count"] = len(artists)      # Add the num of artists to the dict                  
  # Init empty list in data var in dict
  response["data"] = []
  for artist in artists:    
    upcoming_shows = 0          
    for show in artist.shows:
      if show.start_time > datetime.now():# All the upcoming shows
        upcoming_shows += 1
    art = {
      "name" : artist.name,   
      "id" : artist.id,
      "upcoming_shows" : upcoming_shows 
    }
    response["data"].append(art)      
    # Add all to the response["data"] field

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  # Store all the past shows to a var past_shows
  past_shows = list(filter(lambda p: p.start_time < datetime.today(), artist.show))
  # Store all the upcoming shows to a var upcoming_shows
  upcoming_shows = list(filter(lambda u: u.start_time >= datetime.today(), artist.show))
  ven_dict = {
        **artist.__dict__,        
        **{                       
            'past_shows': past_shows,
            'upcoming_shows': upcoming_shows,
            'past_shows_count': len(past_shows),            
            'upcoming_shows_count': len(upcoming_shows)            
        }}

  return render_template('pages/show_artist.html', artist=ven_dict)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)          # Query data based on id
  # separate genres from ","
  form.genres.data = artist.genres.split(",")   

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)

  if form.validate():             
    try:
      artist = Artist.queryget(artist_id)       
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres=",".join(form.genres.data)      
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.website_link = form.website_link.data
      db.session.add(artist)              
      db.session.commit()
      flash("Artist "+artist.name+" was edited succesfully")
    except:
      db.session.rollback()
    finally:
      db.session.close()
  else:
    flash("Artist was not edited!")

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)                 
  form.genres.data = venue.genres.split(",")        
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  if form.validate():          
    try:
      venue = Venue.query.get(venue_id)     
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.genres=",".join(form.genres.data)     
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.seeking_venue = form.seeking_venue.data
      venue.seeking_description = form.seeking_description.data
      venue.website_link = form.website_link.data
      db.session.add(venue)           
      db.session.commit()
      flash("Venue "+form.name.data+" was edited succesfully")
    except Exception:
      db.session.rollback()
    finally:
      db.session.close()
  else:
    flash("Venue was not edited!")
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
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)
  if form.validate():           
    try:
      new_artist = Artist(      
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=",".join(form.genres.data),
        image_link= form.image_link.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data,
      )
      db.session.add(new_artist)    
      db.session.commit()
    # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except Exception:
    # TODO: on unsuccessful db insert, flash an error instead.    
      db.session.rollback()
      flash('Artist' + request.form['name'] + ' was added unsuccessfully !')
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    finally:
      db.session.close()
  else:
    flash("Artist was not added!")

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []       # data list for the final results
  shows = db.session.query(Shows
          ).join(Artist, Artist.id == Shows.artist_id
          ).join(Venue, Venue.id == Shows.venue_id
          ).all()
  
  for show in shows: 
    # Loop through the query, assign to a dictionary
    show_dict = {
      "venue_id": show.venue_id,
      "artist_id": show.artist_id,
      "venue_name": show.venue.name,      
      "artist_name": show.artist.name, 
      "artist_image_link": show.artist.image_link,
      # Change-type the start_time variable to string
      "start_time": show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    }
    data.append(show_dict)      

  return render_template('pages/shows.html', shows=data)

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
  if form.validate():
    try:
      new_show = Shows(                       
        artist_id=form.artist_id.data,
        venue_id=form.venue_id.data,
        start_time=form.start_time.data,
      )
      db.session.add(new_show)                
      db.session.commit()

    # on successful db insert, flash success
      flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except Exception:
      db.session.rollback()
      flash("Show was unsuccessfully added!")

    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
      db.session.commit()
  else:
    flash("Show was not added")
    
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
