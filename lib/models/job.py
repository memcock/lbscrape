import app
db = app.db
from lib.utils import date, encode_id, convert_delta
from datetime import datetime
results = db.Table('results',
		db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
		db.Column('result_set_id', db.Integer, db.ForeignKey('result_set.id')))

class Job(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	complete = db.Column(db.Boolean, default = False)
	# results = db.relationship('Image', secondary=results)
	
	def __init__(self):
		self.complete = False

	@property
	def uuid(self):
		return encode_id(self.id)
	
	def mark_complete(self):
		self.complete = True
		db.session.add(self)
		db.session.commit()
		return self.complete

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

	def expired(self, threshold):
		if self.expires and self.expires < datetime.utcnow():
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
		self.expires = datetime.utcnow() + convert_delta('1h')
