from celery import subtask, group, signature, chord, chain
from ..app import celery
from ..util import check_url, recurse_list
from .database import insert_images, add_to_result_set
from ..database import Image, Result, commit_record
from copy import deepcopy

@celery.task
def collapse_lists(lists):
	print('collapsing list %s'%lists)
	return [ x for x in recurse_list(lists)]
	
@celery.task
def dmap(it, callback):
    # Map a callback over an iterator and return as a group
	sig = signature(callback)
	return group(signature(deepcopy(sig)).clone((arg,)) for arg in it)()

@celery.task
def dchain(it, links):
	# Maps a iterator over a chain
	links = [signature(x) for x in links]
	first = links[0]
	chains = []
	for item in it:
		sig = first.clone(item)
		ch = chain(sig, *links[1:])
		chains.append(ch)
	return group(x for x in chains)()

@celery.task
def to_chord(it, links = [], callback = None):
	'''
		Map a task over a iterator and returns a chord using callback
	'''
	# callback = signature(callback)
	links = [signature(x) for x in links]
	first = links[0]
	chains = []
	for item in it:
		sig = first.clone(item)
		ch = chain(sig, *links[1:])
		chains.append(ch)
	ch = chord(x for x in chains)
	if callback:
		return ch(signature(callback))
	return ch()

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
	
@celery.task
def update_results(results, rsid):
	print(len(results), results)
	imgs = [i for i in [Image.create(**r) for r in results] if i]
	Result.add_to(rsid, imgs)
	return results

@celery.task
def check_results(results, rsid, subreddit):
	rS = Result.get(rsid)
	if not rS.complete:
		print('%s is stuck'%rsid)
		rS.stuck = True
	return commit_record(rS)

