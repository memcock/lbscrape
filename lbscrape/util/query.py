# import lib.database as database
# import lib.reddit as reddit
# from datetime import datetime, timezone, timedelta
# import lib.utils as utils
# from .util import time


# def new_posts(nPosted, nScanned, limit):
# 	if not nScanned:
# 		return nPosted - limit, nPosted
# 	elif nPosted > nScanned:
# 		stop = max_delta(nPosted, nScanned, limit)
# 		return nPosted, stop
# 	return None

# def old_posts(oScanned, created, limit):
# 	if oScanned > created:
# 		stop = min_delta(oScanned, created, limit)
# 		return oScanned, stop
# 	return None

# def new_unscanned(subreddit, limit):
# 	'''
# 		returns time range to scan for new posts
# 		up to limit in length
# 	'''
# 	newest_posted = reddit.details(subreddit.source).get('newest')
# 	newest_scanned = subreddit.newest
# 	if not newest_scanned:
# 		# If we haven't scanned this subreddit before
# 		# just scan the previous 1 day of posts
# 		start = newest_posted
# 		stop = newest_posted - limit
# 	elif newest_posted > newest_scanned:
# 		start = newest_scanned			# just scan limit
# 		if newest_posted - newest_scanned > limit: 
# 			stop = newest_scanned + limit	# If theres more than limit time to scan
# 		else:
# 			stop = newest_posted			# Otherwise scan all new
# 	else:
# 		return None
# 	subreddit.newest = stop
# 	return (start, stop)

# def old_unscanned(subreddit, limit):
# 	'''
# 		return time range to scan for old posts
# 		up to limit in length
# 	'''
# 	oldest_scanned = subreddit.oldest
# 	if not oldest_scanned:
# 		if subreddit.newest:
# 			oldest_scanned = subreddit.newest
# 		else:
# 			return None
# 	if oldest_scanned > subreddit.created: # scan remaining old posts
# 		start = oldest_scanned
# 		if oldest_scanned - subreddit.created > limit:
# 			stop = oldest_scanned - limit
# 		else:
# 			stop = subreddit.created
# 	else:
# 		return None
# 	subreddit.oldest = stop
# 	return (start, stop)

# def unscanned(name, limit = '1d'):
# 	'''
# 		return a list of time ranges to scan for new posts
# 	'''
# 	limit = utils.convert_delta(limit)
# 	subreddit = database.get_subreddit(name)
# 	segments = []
# 	segments.append(new_unscanned(subreddit, limit))
# 	segments.append(old_unscanned(subreddit, limit))
# 	database.commit_record(subreddit)
# 	return [x for x in segments if not x is None]

# def split_unscanned(unscanned, interval = '24h'):
# 	'''
# 		splits a list of time ranges into segments at most interval in length
# 	'''
# 	delta = utils.convert_delta(interval)
# 	segs = []
# 	for start, end in unscanned:
# 		for seg_start, seg_end in utils.iter_by_delta(start, end, delta):
# 			segs.append((int(seg_start.timestamp()), int(seg_end.timestamp())))
# 	return segs

# def scan_segments(subreddit, interval = '24h'):
# 	return split_unscanned(unscanned(subreddit), interval)