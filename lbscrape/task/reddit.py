import app
from ..util import time
from ..reddit import images, newest
from ..database import Subreddit, commit_record

def new_posts(nPosted, nScanned, limit):
	if not nScanned:
		return nPosted - limit, nPosted
	elif nPosted > nScanned:
		stop = max_delta(nPosted, nScanned, limit)
		return nPosted, stop
	return None

def old_posts(oScanned, created, limit):
	if not oScanned:
		return None
	if oScanned > created:
		stop = min_delta(oScanned, created, limit)
		return oScanned, stop
	return None

@app.celery.task
def GetSegments(subreddit, interval = '24h'):
	sub = Subreddit.get(subreddit)
	nPosted = newest(subreddit)
	nScanned = sub.newest
	newPosts = new_posts(nPosted, nScanned, time.convert_delta(limit))
	oScanned = sub.oldest if sub.oldest else nScanned
	oldPosts = old_posts(oScanned, sub.created, time.convert_delta(limit))
	if newPosts:
		sub.newest = newPosts[1]
	if oldPosts:
		sub.oldest = oldPosts[1]
	commit_record(sub)
	posts = [ p for p in [newPosts, oldPosts] if p]
	segs = []
	for st, sp in posts:
		for start, stop in time.iter_by_delta(st, sp):
			segs.append(start.timestamp(), stope.timestamp())
	for seg in segs:
		print(seg) # TODO: convert to logging
	return [x.timestamp(), y.timestamp() for x,y in seg]


@app.celery.task
def GetLinks(start, stop, subreddit):
	return [submission_to_dict(url) for url in images(subreddit, start, stop)]

