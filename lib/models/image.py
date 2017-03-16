import app
db = app.db
from lib.utils import date, check_url, convert_delta, utc_time
from datetime import datetime

class Image(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	fullname = db.Column(db.Text, unique = True)
	url = db.Column(db.Text)
	created = db.Column(db.DateTime)
	subreddit_id = db.Column(db.Text, db.ForeignKey('subreddit.source'))
	checked = db.Column(db.DateTime)

	def __init__(self, fullname, url, created, subreddit):
		self.fullname = fullname
		self.url = url
		self.created = created
		self.subreddit = subreddit
		self.checked = datetime.utc_now()

	@property
	def as_dict(self):
		return {
			'fullname': self.fullname,
			'url': self.url,
			'created': self.created.timestamp(),
			'subreddit': self.subreddit.source
		}

	def check(self, threshold):
		if convert_delta(threshold) < datetime.utcnow() - self.checked :
			if not check_url(self.url):
				pass # delete the image here
				# return False
			self.checked = datetime.utcnow()
		return True
