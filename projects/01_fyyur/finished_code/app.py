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
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
def db_setup(app):
    app.config.from_object('config')
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    upcoming_counter = db.Column(db.Integer, default=0)
    seekingDescription = db.Column(db.String(500))
    website = db.Column(db.String(120))
    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()




class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    address = db.Column(db.String(120))
    website = db.Column(db.String(120))
    upcoming_counter = db.Column(db.Integer, default=0)
    seekingVenue = db.Column(db.Boolean)
    seekingDescription = db.Column(db.String(500))
    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.update(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  recentVenues = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
  recentArtists = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
  return render_template('pages/home.html',venues = recentVenues, artists = recentArtists)

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')

def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = db.session.query(Venue.city,Venue.state).group_by(Venue.state,Venue.city).all()
  data = []
  for area in venues:
    venues = db.session.query(Venue.id,Venue.name,Venue.upcoming_counter).filter(Venue.city==area[0],Venue.state==area[1]).all()
    data.append({
        "city": area[0],
        "state": area[1],
        "venues": []
    })
    for venue in venues:
      data[-1]["venues"].append({
              "id": venue[0],
              "name": venue[1],
              "num_upcoming_shows":venue[2]
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(results),
    "data": []
    }
  for venue in results:
    response["data"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": venue.upcoming_counter
      })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  prevShow = []
  upcoming_shows = []
  shows = venue.shows
  for show in shows:
    show_info ={
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": str(show.start_time)
    }
    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      prevShow.append(show_info)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seekingDescription": venue.seekingDescription,
    "image_link": venue.image_link,
    "prevShow": prevShow,
    "upcoming_shows": upcoming_shows,
    "prevShow_count": len(prevShow),
    "upcoming_counter": len(upcoming_shows)
  }
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
      venue_form = VenueForm(request.form)
      new_venue = Venue(
        name=venue_form.name.data,
        genres=','.join(venue_form.genres.data),
        address=venue_form.address.data,
        city=venue_form.city.data,
        state=venue_form.state.data,
        phone=venue_form.phone.data,
        facebook_link=venue_form.facebook_link.data,
        image_link=venue_form.image_link.data)
      new_venue.add()
  # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except Exception as ex:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    

  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get_or_404(venue_id)
    if len(venue.shows):
      flash('Unable to remove the venue on which shows are held!')
      return redirect(url_for('show_venue', venue_id = venue_id))
      data = {}
      data['name'] = venue.name
  
      venue.genres = []
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + data['name'] + ' has been deleted.')
  except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Venue ' + data['name'] + ' could not be deleted.')
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  finally:
      db.session.close()
  return redirect(url_for('index'))
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('name').all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form.get('search_term')
  data = Artist.query.with_entities(Artist.id, Artist.name, Artist.city, Artist.state).filter(Artist.name.ilike("%" + search + "%") | Artist.city.ilike("%" + search + "%") | Artist.state.ilike("%" + search + "%")).order_by('id').all()

  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  prevShow = []
  upcoming_shows = []
  for show in shows:
    show_info = {
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": str(show.start_time)
    }
    if(show.upcoming):
      upcoming_shows.append(show_info)
    else:
      prevShow.append(show_info)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','), 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seekingVenue": artist.seekingVenue,
    "seekingDescription":artist.seekingDescription,
    "image_link": artist.image_link,
    "prevShow": prevShow,
    "upcoming_shows": upcoming_shows,
    "prevShow_count": len(prevShow),
    "upcoming_counter": len(upcoming_shows)
  }
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
   form = ArtistForm()
   if form.validate_on_submit():
       try:
           artist = Artist()
           form.populate_obj(artist)
           db.session.commit()
           flash('Artist ' + request.form['name'] + ' was successfully updated!')
       except:
           db.session.rollback()
           print(sys.exc_info())
           flash('Unable to write data!')
       finally:
           db.session.close()
   else:
       flash('Check your data!')
       return render_template('forms/edit_venue.html', form=form, venue=venue)
  
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueEditForm()
  venue = db.session.query(Venue).filter_by(id=venue_id).first()
  if venue:
        try:
            venue.name = form.name.data,venue.city = form.city.data,venue.state = form.state.data,venue.address = form.address.data,venue.phone = form.phone.data,venue.seekingDescription = form.seekingDescription.data,venue.image_link = form.image_link.data,venue.facebook_link = form.facebook_link.data,venue.website = form.website.data,venue.genres = form.genres.data
            db.session.add(venue)
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully updated.')
        except:
            flash('Something went wrong. Venue ' +
                  request.form['name'] + ' could not be updated.')
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
  try:
    new_venue = Venue(
      name=request.form['name'],
      genres=request.form.getlist('genres'),
      address=request.form['address'],
      city=request.form['city'],
      state=request.form['state'],
      phone=request.form['phone'],
      website=request.form['website'],
      facebook_link=request.form['facebook_link'],
      image_link=request.form['image_link'],
      seeking_talent=request.form['seeking_talent'],
      description=request.form['seekingDescription'],
    )
    #insert new venue records into the db
    Venue.insert(new_venue)
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except SQLAlchemyError as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  showRel = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  objects = db.session.query(Show).all()
  show = {}
  for obj in objects:
    show["venue_id"] = obj.venue_id
    show["venue_name"] = obj.venue.name
    show["artist_id"] = obj.artist_id
    show["artist_name"] = obj.artist.name
    show["artist_image_link"] = obj.artist.image_link
    show["start_time"] = obj.start_time
    data.append(show)
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
  newShow = Show()
  newShow.artist_id = request.form['artist_id']
  newShow.venue_id = request.form['venue_id']
  dateAndTime = request.form['start_time'].split(' ')
  DTList = dateAndTime[0].split('-')
  DTList += dateAndTime[1].split(':') 
  for i in range(len(DTList)):
    DTList[i] = int(DTList[i])
  newShow.start_time = datetime(DTList[0],DTList[1],DTList[2],DTList[3],DTList[4],DTList[5])
  now = datetime.now()
  newShow.upcoming = (now < newShow.start_time)
  try:
    db.session.add(newShow)
    # update venue and artist table
    artist = Artist.query.get(newShow.artist_id)
    venue = Venue.query.get(newShow.venue_id)
    if(newShow.upcoming):
      artist.upcoming_counter += 1;
      venue.upcoming_counter += 1;
    else:
      artist.prevShow_count += 1;
      venue.prevShow_count += 1;
    # on successful db insert, flash success
    db.session.commit()
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
  except:
    db.session.rollback()
   
    flash('Show could not be listed. please make sure that your ids are correct')
  finally:
    db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('index'))

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
