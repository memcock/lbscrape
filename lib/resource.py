from flask_restful import Resource, fields, marshal, abort
from flask import jsonify, request
from lib.tasks import find_images
import lib.utils as utils
import lib.database as database
from celery.result import AsyncResult
import lib.reddit as reddit
from flask_restful import reqparse
from config import getLogger

_log = getLogger(__name__)

job_resource_fields = {
	'uuid': fields.String,
	'complete': fields.Boolean
}

class Subreddit(Resource):
	def get(self, subreddit):
		wanted = request.args.get('wanted', default = 10, type = int)
		exclude = request.args.getlist('exclude')
		_log.debug(exclude)
		job = find_images(subreddit, wanted, exclude)
		return marshal(job, job_resource_fields, envelope='result'), 202

class Queue(Resource):
	def get(self, job_id):
		job = database.get_job(utils.decode_id(job_id))
		if not job.complete:
			return dict(result={'complete':False}), 202
		return dict(result={'complete':True}), 303		

class Result(Resource):
	def get(self, job_id):
		job = database.get_job(utils.decode_id(job_id))
		if job.complete:
			results = [result.as_dict for result in job.results]
			return dict(result={'links': results}), 200
		return dict(result={'complete':False}), 412		

class Check(Resource):
	def get(self, subreddit):
		return dict(valid = reddit.check(subreddit))
