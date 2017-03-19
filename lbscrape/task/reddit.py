from ..app import celery
from ..util import time, db
from ..reddit import images, newest
from ..database import Subreddit, commit_record
from prawcore.exceptions import PrawcoreException

def new_posts(nPosted, nScanned, limit):
	if not nScanned:
		return nPosted - limit, nPosted
	elif nPosted > nScanned:
		stop = time.max_delta(nPosted, nScanned, limit)
		return nPosted, stop
	return None

def old_posts(oScanned, created, limit):
	if not oScanned:
		return None
	if oScanned > created:
		stop = time.min_delta(oScanned, created, limit)
		return oScanned, stop
	return None

@celery.task
def GetSegments(subreddit, interval = '24h'):
	sub = Subreddit.get(subreddit)
	nPosted = time.utc_time(newest(subreddit).created_utc)
	nScanned = sub.newest
	newPosts = new_posts(nPosted, nScanned, time.convert_delta(interval))
	oScanned = sub.oldest if sub.oldest else nScanned
	oldPosts = old_posts(oScanned, sub.created, time.convert_delta(interval))
	if newPosts:
		sub.newest = newPosts[1]
	if oldPosts:
		sub.oldest = oldPosts[1]
	commit_record(sub)
	posts = [ p for p in [newPosts, oldPosts] if p]
	segs = []
	for st, sp in posts:
		for start, stop in time.iter_by_delta(st, sp, time.convert_delta('12h')):
			segs.append((start.timestamp(), stop.timestamp()))
	for seg in segs:
		print(seg) # TODO: convert to logging
	return segs


@celery.task(autoretry_for = (PrawcoreException,), default_retry_delay = 5)
def GetLinks(start, stop, subreddit):
	# PrawcoreException
	return [db.submission_to_dict(url) for url in images(subreddit, start, stop)]

