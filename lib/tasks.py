import app
import lib.reddit as reddit
import lib.query as query
from celery import subtask, group, signature, chord
from lib.utils import submission_to_dict, collapse_double_list, utc_time
import lib.database as database

def create_scrape_job(subreddit, wanted, job_id):
	task = (GetSegments.s(subreddit) | 
			to_chord.s(
				GetLinks.s(subreddit),
				check_progress.s(subreddit, job_id, wanted)))
	return task
		

def find_images(subreddit, wanted, exclude = []):
	job = database.create_job()
	images = database.get_images(subreddit, wanted, exclude)
	database.add_results_to_job(job, images)
	if len(images) < wanted:
		needed = wanted - len(images)
		create_scrape_job(subreddit, needed, job.id)()
	else:
		job.complete = True
		database.commit_record(job)
	return job

@app.celery.task
def GetSegments(subreddit, interval = '24h'):
	segs = query.scan_segments(subreddit, interval)
	for seg in segs:
		print(utc_time(seg[0]), utc_time(seg[1]))
	return segs


@app.celery.task
def GetLinks(start, stop, subreddit):
	return [submission_to_dict(url) for url in reddit.images(subreddit, start, stop)]

@app.celery.task
def dmap(it, callback):
    # Map a callback over an iterator and return as a group
	return group(subtask(callback).clone(arg) for arg in it)()

@app.celery.task
def to_chord(it, group_task, callback):
	'''
		Map a task over a iterator and returns a chord using callback
	'''
	callback = signature(callback)
	return chord(subtask(group_task).clone(arg) for arg in it)(callback)

@app.celery.task
def check_progress(results, subreddit, job_id, wanted):
	print(results)
	results = collapse_double_list(results)
	print(results)
	images = [database.create_image(**result) for result in results]
	images = [x for x in images if x]
	database.add_results_to_job(job_id, images[:wanted])
	print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	print('found %i images, wanted %i'%(len(images), wanted))
	print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	if len(images) < wanted:
		needed = wanted - len(images)
		create_scrape_job(subreddit, needed, job_id)()
	else:
		 mark_complete.delay(job_id)

@app.celery.task
def mark_complete(job_id):
	job = database.get_job(job_id)
	job.mark_complete()