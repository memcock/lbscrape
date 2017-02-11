import app
db = app.db
from lib.utils import date, encode_id

results = db.Table('results',
		db.Column('image_id', db.Integer, db.ForeignKey('image.id')),
		db.Column('job_id', db.Integer, db.ForeignKey('job.id')))

class Job(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	complete = db.Column(db.Boolean, default = False)
	results = db.relationship('Image', secondary=results)
	
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