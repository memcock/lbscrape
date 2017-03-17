from celery import subtask, group, signature, chord
from ..app import celery
from ..util import check_url, recurse_list
from .database import insert_images, add_to_result_set

@celery.task
def collapse_lists(lists):
	return [ x for x in recurse_list(lists)]
	
@celery.task
def dmap(it, callback):
    # Map a callback over an iterator and return as a group
	return group(subtask(callback).clone(arg) for arg in it)()

@celery.task
def to_chord(it, group_task, callback):
	'''
		Map a task over a iterator and returns a chord using callback
	'''
	callback = signature(callback)
	return chord(subtask(group_task).clone(arg) for arg in it)(callback)

@celery.task
def checkUrl(link):
	return link, check_url(link['url'])

@celery.task
def checkUrls(images):
	checked = [ image for image in images if check_url(image['url']) ]
	return checked


@celery.task
def update_results_set(results, rsid, wanted):
	results = collapse_double_list(results)
	images = [x for x in images if x] # Remove nulls
	needed = images[:wanted]
	extra = images[wanted + 1:]
	if needed:
		add_to_result_set(needed, rsid).delay()
	if extra:
		insert_images(extra).delay()
	
