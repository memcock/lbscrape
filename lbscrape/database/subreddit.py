from ..models import Subreddit as SubredditModel
from .func import commit_record
from ..reddit import details

class Subreddit:
	@staticmethod
	def get(id, create = True):
		if isinstance(id, int):
			sub = SubredditModel.query.get(id)
		elif isinstance(id, str):
			id = id.lower()
			sub = SubredditModel.query.filter_by(source = id).all()
			if len(sub):
				sub = sub[0]
			if not sub and create:
				created = details(id).get('created', 0)
				sub = SubredditModel(id, created)
				return sub if commit_record(sub) else None
		else:
			sub = None
		return sub

	@staticmethod
	def set_oldest(id, timestamp):
		sub = Subreddit.get(id)
		if sub:
			sub.oldest = timestamp
			commit_record(sub)
	
	@staticmethod
	def set_newest(id, timestamp):
		sub = Subreddit.get(id)
		if sub:
			sub.newest = timestamp
			commit_record(sub)
