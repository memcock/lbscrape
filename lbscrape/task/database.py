import app
from ..database import Image, Result

@app.celery.task
def insert_images(links):
	for link in links:
		Image.create(**link)

@app.celery.task
def add_to_result_set(images, id):
	Result.add_to(id, images)

@app.celery.task
def mark_complete(job_id):
	# job = get_job(job_id)
	# job.mark_complete()
	pass