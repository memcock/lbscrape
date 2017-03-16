import app
from ..database import create_image, get_job, add_results_to_result_set

@app.celery.task
def insert_images(links):
	for link in links:
		create_image(**link)

@app.celery.task
def add_to_result_set(images, id):
	add_results_to_result_set(images, id)

@app.celery.task
def mark_complete(job_id):
	job = get_job(job_id)
	job.mark_complete()