from ..models import SubredditModel
from .func import commit_record


class Subreddit:
	@staticmethod
	def get(id, create = True):
		if isinstance(id, int):
			sub = SubredditModel.query.get(id)
		elif isinstance(id, str):
			id = id.lower()
			sub = SubredditModel.query.where(SubredditModel.source == id).one()
			if not sub and create:
				created = details(name).get('created', 0)
				sub = models.Subreddit(name, created)
				return True if commit_record(sub) else None
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