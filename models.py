from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()

# Models for Artists, Venues, Shows

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.Integer())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(120))           
    website_link = db.Column(db.String(120))     
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))  
    show = db.relationship('Shows', backref='venue', lazy=True)

    def __repr__(self):
      return f"Venue ID: {self.id}, Venue Name: {self.name}, Venue City: {self.city}, Venue State: {self.state}, Venue Address: {self.address}, Venue Phone: {self.phone}, Venue Image-Link: {self.image_link}, FB-Link: {self.facebook_link}, Venue Genres: {self.genres}, Venue Website-link: {self.website_link}, Venue Seek talent: {self.seeking_talent}"

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.Integer())
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(120))       
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500)) 
    show = db.relationship('Shows', backref='artist', lazy=True)

    def __repr__(self):
      return f"Venue ID: {self.id}, Venue Name: {self.name}, Venue City: {self.city}, Venue State: {self.state}, Venue Address: {self.address}, Venue Phone: {self.phone}, Venue Image-Link: {self.image_link}, FB-Link: {self.facebook_link}, Venue Genres: {self.genres}, Venue Website-link: {self.website_link}, Venue Seek Venue: {self.seeking_venue}"

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)  
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'),nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'),nullable=False)

    def __repr__(self):
      return f"Show ID: {self.id}, Show Start: {self.start_time}, Show Artist: {self.artist_id}, Show Venue: {self.venue_id}"
