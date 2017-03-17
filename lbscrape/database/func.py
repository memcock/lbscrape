
from ..app import db

def commit_record(record):
	try:
		db.session.add(record)
		db.session.commit()
	except IntegrityError:
		db.session.rollback()
		return False
	return True