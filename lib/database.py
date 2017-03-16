import app
from sqlalchemy.exc import IntegrityError
import lib.models as models
from .reddit import details
import lib.utils as utils

def commit_record(record):
	try:
		app.db.session.add(record)
		app.db.session.commit()
	except IntegrityError:
		app.db.session.rollback()
		return False
	return True

def get_subreddit(name, create = True):
	name = name.lower()
	sub = list(models.Subreddit.query.filter_by(source=name))
	if not sub and create:
		created = details(name).get('created', 0)
		sub = models.Subreddit(name, created)
		try:
			app.db.session.add(sub)
			app.db.session.commit()
		except IntegrityError:
			app.db.session.rollback()
			return get_subreddit(name, create)
		else:
			return sub
	return sub.pop()

def build_exclusion_filter(query, exclude):
	for x in exclude:
		query = query.filter(models.Image.fullname != x)
	return query

def get_images(subreddit, limit = 10, exclude = []):
	sub = get_subreddit(subreddit)
	query = build_exclusion_filter(sub.images, exclude)
	images = query.limit(limit).all()
	return images

def create_image(fullname = None, url = None, created = None, subreddit = None):
	subreddit = get_subreddit(subreddit)
	created = utils.utc_time(created)
	img = models.Image(fullname, url, created, subreddit)
	status = commit_record(img)
	if not status:
		return None
	return img

def create_job():
	job = models.Job()
	app.db.session.add(job)
	app.db.session.commit()
	return job

def get_job(job_id):
	job = models.Job.query.get(job_id)
	return job

def create_result_set(length):
	rS = models.ResultSet(length)
	if commit_record(rS):
		return rS
	return None

def get_result_set(rsid):
	rS = models.ResultSet.query.get(rsid)
	return rS

def add_results_to_result_set(rsid, results):
	rS = get_result_set(rsid)
	for result in results:
		rS.results.append(result)
	commit_record(result)

def add_results_to_job(job, results):
	if isinstance(job, int):
		job = get_job(job)
	if not isinstance(results, list):
		results = [results,]
	for result in results:
		job.results.append(result)
	app.db.session.add(job)
	app.db.session.commit()
