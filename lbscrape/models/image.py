from ..app import db
# db = app.db
from ..util import time, check_url 

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
		self.checked = time.now()

	def __repr__(self):
		args = (
			self.fullname,
			self.subreddit,
			self.created,
			self.checked
			)
		return '<Image fullname: %s, sub: %s, created: %s, checked: %s>'
		
	@property
	def as_dict(self):
		return {
			'fullname': self.fullname,
			'url': self.url,
			'created': self.created.timestamp(),
			'subreddit': self.subreddit.source
		}

	def check(self, threshold):
		if time.convert_delta(threshold) < time.now() - self.checked :
			if not check_url(self.url):
				pass # delete the image here
				# return False
			self.checked = time.now()
		return True
