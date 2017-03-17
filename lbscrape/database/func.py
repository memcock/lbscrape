
import app

def commit_record(record):
	try:
		app.db.session.add(record)
		app.db.session.commit()
	except IntegrityError:
		app.db.session.rollback()
		return False
	return True