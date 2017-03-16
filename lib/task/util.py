import app
from celery import subtask, group, signature, chord
from ..utils import check_url
from .database import insert_images, add_to_result_set

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
def checkUrl(link):
	return link, check_url(link['url'])

@app.celery.task
def checkUrls(images):
	checked = [ image for image in images if check_url(image['url']) ]
	return checked


@app.celery.task
def update_results_set(results, rsid, wanted):
	results = collapse_double_list(results)
	images = [x for x in images if x] # Remove nulls
	needed = images[:wanted]
	extra = images[wanted + 1:]
	if needed:
		add_to_result_set(needed, rsid).delay()
	if extra:
		insert_images(extra).delay()
	
