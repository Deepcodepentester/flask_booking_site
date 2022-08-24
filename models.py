#from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
db = SQLAlchemy(app)
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    website = db.Column(db.String(120),nullable=False)
    seeking_venue= db.Column(db.String(120),default=False)
    seeking_description = db.Column(db.String(120),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now(),nullable=False)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String(120)),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    website = db.Column(db.String(120),nullable=False)
    seeking_venue= db.Column(db.String(120),default=False)
    seeking_description = db.Column(db.String(120),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now(),nullable=False)
    venues = db.relationship('Venue', secondary= 'show',backref=db.backref('artists', lazy=True))

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'),nullable=False )
    venue_id =db.Column( db.Integer, db.ForeignKey('venue.id'),nullable=False )
    starter_time =  db.Column(db.DateTime,nullable=False )
    # v = db.relationship('Venue',backref='list',lazy=True)
    # a=db.relationship('Artist',backref='list',lazy=True)
