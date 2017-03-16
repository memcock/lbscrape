from flask_restful import Resource, fields, marshal, abort
from flask import jsonify, request
# from lib.tasks import find_images
import lib.utils as utils
import lib.database as database
from celery.result import AsyncResult
import lib.reddit as reddit
from flask_restful import reqparse
from config import getLogger
import lib.models as models
from .task import Scan
_log = getLogger(__name__)

ResultSet_resource_fields = {
	'uuid': fields.String,
	'complete': fields.Boolean
}

class Subreddit(Resource):
	def get(self, subreddit):
		wanted = request.args.get('wanted', default = 10, type = int)
		exclude = request.args.getlist('exclude')
		_log.debug(exclude)
		prefetch_images = self.load_images(subreddit, wanted, exclude)
		rS = self.result_set(wanted, prefetch_images)
		if not rS.complete:
			Scan(subreddit, wanted - len(prefetch_images), rS.id)()
		return marshal(rS, ResultSet_resource_fields, envelope='result'), 202

	def load_images(self, subreddit, wanted, exclude):
		images = database.get_images(subreddit, wanted, exclude)
		return images

	def result_set(self, length, results = []):
		return models.ResultSet(length, *results)

class Queue(Resource):
	"""
		Queries for a Results object for job_id
	"""
	def get(self, rsid):
		rS = database.get_result_set(utils.decode_id(rsid))
		if not rS.complete:
			return dict(result={'complete':False, 'progress':rS.progress}), 202
		return dict(result={'complete':True, 'progress':rS.progress}), 303		

class Result(Resource):
	def get(self, rsid):
		rS = database.get_result_set(utils.decode_id(rsid))
		if rS.complete:
			rS.mark()
			results = [result.as_dict for result in rS.results]
			return dict(result={'links': results}), 200
		return dict(result={'complete':False}), 412		

class Check(Resource):
	def get(self, subreddit):
		return dict(valid = reddit.check(subreddit))
