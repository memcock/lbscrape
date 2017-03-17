from ..models import Image as ImageModel
from .func import commit_record
from .subreddit import Subreddit
from ..util import time

class Image:
	@staticmethod
	def get(rsid):
		'''
			Return a Image given its id or None
		'''
		return ImageModel.query.get(rsid)
		
	@staticmethod
	def create(fullname = None, url = None, created = None, subreddit = None):
		''' 
			Creates a Image of length, optionaly adding results
		'''
		subreddit = Subreddit.get(subreddit)
		created = time.utc_time(created)
		img = ImageModel(fullname, url, created, subreddit)
		status = commit_record(img)
		return img if status else None

	@staticmethod
	def build_exclusion_filter(query, exclude):
		for x in exclude:
			query = query.filter(Image.fullname != x)
		return query

	@staticmethod
	def search(subreddit, limit = 10, exclude = []):
		subreddit = Subreddit.get(subreddit)
		query = ImageModel.build_exclusion_filter(sub.images, exclude)
		return query.limit(limit).all()