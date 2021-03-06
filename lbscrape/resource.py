from flask_restful import Resource, fields, marshal
from flask import request
# from lib.tasks import find_images
from .util.db import decode_id
from .database import Result, Image, Subreddit, commit_record
ResultDB, ImageDB, SubredditDB = Result, Image, Subreddit
from .reddit import check as check_subreddit
from .config import getLogger
from .task import Scan
_log = getLogger(__name__)

ResultSet_resource_fields = {
	'uuid': fields.String,
	'complete': fields.Boolean
}

class Dummy200(Resource):
	def get(self):
		return {}, 200
		
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
		images = ImageDB.search(subreddit, wanted, exclude)
		return images

	def result_set(self, length, results = []):
		return ResultDB.create(length, *results)

class Queue(Resource):
	"""
		Queries for a Results object for job_id
	"""
	def get(self, rsid):
		rS = ResultDB.get(decode_id(rsid))
		_log.debug('Checking status for %s'%rsid)
		if rS.stuck:
			_log.debug('Found stuck result')
			s = Scan._load(rS.id)
			if s:
				_log.debug('Starting new Scan')
				s()
				rS.stuck = False
				commit_record(rS)
			else:
				_log.error('Error loading Scan')
				rS.stuck = False
				commit_record(rS)
			return dict(result={'complete':False, 'progress':rS.progress}), 202
		if not rS.complete:
			_log.debug('Incomplete Results %s'%rsid)
			return dict(result={'complete':False, 'progress':rS.progress}), 202
	
		_log.debug('Complete Results %s'%rsid)
		return dict(result={'complete':True, 'progress':rS.progress}), 303		

class Result(Resource):
	def get(self, rsid):
		rS = ResultDB.get(decode_id(rsid))
		if rS.complete:
			rS.mark() # mark results with the configured expiry time
			results = [result.as_dict for result in rS.results]
			return dict(result={'links': results}), 200
		return dict(result={'complete':False}), 412		

class Check(Resource):
	def get(self, subreddit):
		if not SubredditDB.get(subreddit, create = False):
			return dict(valid = check_subreddit(subreddit))
		return dict(valid = True)
