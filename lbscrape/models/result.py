import app
db = app.db
from .util.db import encode_id
from .util import time

results = db.Table('results',
		db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
		db.Column('result_set_id', db.Integer, db.ForeignKey('result_set.id')))

class ResultSet(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	expires = db.Column(db.DateTime)
	length = db.Column(db.Integer)
	results = db.relationship('Image', secondary=results,
				backref = 'result_sets')

	def __init__(self, length, *args):
		self.length = length
		for args in args:
			self.results.append(arg)
			
	def __repr__(self):
		return '<ResultSet id: %s, lenght: %s, results: %s, expires: %s>'%(self.id, self.length,
																	self.results, sef.expires)
	@property
	def expired(self):
		if self.expires and self.expires < time.now():
			return True
		return False
	
	@property
	def progress(self):
		return len(self.results) / self.length

	@property
	def complete(self):
		return len(self.results) >= self.length

	@property
	def uuid(self):
		return encode_id(self.id)

	def mark(self):
		self.expires = time.now() + convert_delta('1h')
