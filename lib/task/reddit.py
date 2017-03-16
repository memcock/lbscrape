import app
import lib.query as query
from ..utils import utc_time
from ..reddit import images

@app.celery.task
def GetSegments(subreddit, interval = '24h'):
	segs = query.scan_segments(subreddit, interval)
	for seg in segs:
		print(utc_time(seg[0]), utc_time(seg[1])) # TODO: convert to logging
	return segs


@app.celery.task
def GetLinks(start, stop, subreddit):
	return [submission_to_dict(url) for url in images(subreddit, start, stop)]




	
def check_progress(results, subreddit, job_id, wanted):
	results = collapse_double_list(results)
	checked = []
	for num in range(len(results)):
		if check_url(results[num]['url']):
			checked.append(results[num])
		if len(checked) >= wanted: 					# We only check as many images as we need
			check_extra_images(results[num + 1:])()	# then schedule the rest to be checked later
			break
	# checked = [x for x in results[:wanted] if check_url(x['url'])]
	# print(checked)
	images = [database.create_image(**result) for result in checked]
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