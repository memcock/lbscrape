import app
db = app.db
from lib.utils import date

class Subreddit(db.Model):
	id = db.Column(db.Integer, primary_key= True)
	source = db.Column(db.Text, unique = True)
	created = db.Column(db.DateTime, default = 0) # Subreddit creation date
	newest = db.Column(db.DateTime) # Latest time stamp scanned for posts
	oldest = db.Column(db.DateTime) # Oldest time stamp scanned for posts
	images = db.relationship('Image', backref='subreddit', lazy='dynamic')

	def __init__(self, source, created):
		self.source = source
		self.created = created
		