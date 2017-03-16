import app

import lib.models as models
import lib.utils as utils

def prune_results():
	for job in models.Job.query.all():
		app.db.session.delete(job)

def prune_dead_images():
	for image in models.image.Image.query.all():
		print('Checking %s %s - %s'%(image.subreddit.source, image.fullname, image.url))
		if not utils.check_url(image.url):
			print('Pruning associated results')
			for res in app.db.session.query(models.job.results).filter(models.job.results.c.image_id==image.id).all():
				app.db.session.delete(res)
			print('Pruning %s %s - %s'%(image.subreddit.source, image.fullname, image.url))
			app.db.session.delete(image)
