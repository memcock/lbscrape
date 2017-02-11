import app
db = app.db
from lib.utils import date

class Image(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.Text, unique = True)
	url = db.Column(db.Text)
	created = db.Column(db.DateTime)
	subreddit_id = db.Column(db.Text, db.ForeignKey('subreddit.source'))

	def __init__(self, fullname, url, created, subreddit):
		self.fullname = fullname
		self.url = url
		self.created = created
		self.subreddit = subreddit

	@property
	def as_dict(self):
		return {
			'fullname': self.fullname,
			'url': self.url,
			'created': self.created.timestamp(),
			'subreddit': self.subreddit.source
		}