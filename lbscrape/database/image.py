from ..models import Image as ImageModel
from sqlalchemy.sql.expression import func
from .func import commit_record
from .subreddit import Subreddit
from ..util import time

class Image:
	@staticmethod
	def get(imgid):
		'''
			Return a Image given its id or None
		'''
		return ImageModel.query.get(imgid)
		
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
			query = query.filter(ImageModel.fullname != x)
		return query

	@staticmethod
	def search(subreddit, limit = 10, exclude = []):
		subreddit = Subreddit.get(subreddit)
		query = Image.build_exclusion_filter(subreddit.images, exclude)
		return query.order_by(func.random()).limit(limit).all()