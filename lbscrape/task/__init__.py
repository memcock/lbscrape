from .reddit import GetLinks, GetSegments
from .util import to_chord, checkUrls, update_results, collapse_lists, dmap, dchain, check_results
from celery import chain
from ..database import Result, commit_record

class Task:
	def _execute(self, *args, **kwargs):
		pass 
	def __call__(self, *args, **kwargs):
		ar, kw = self._before_task(*args, **kwargs)
		return self._execute(*ar, **kw)

	def _dump(self, *args, to_rsid = True, **kwargs):
		data = { arg: getattr(self, arg, None) for arg in args }
		data.update(kwargs)
		if 'rsid' in data:
			res = Result.get(data.pop('rsid'))
			if to_rsid:
				res._task = data
				commit_record(res)
		return data

	@staticmethod
	def _load(rsid):
		res = Result.get(rsid)
		return res._task

	def _before_task(self, *args, **kwargs):
		return args, kwargs
	
class Scan(Task):
	def __init__(self, subreddit, wanted, rsid):
		self.subreddit = subreddit
		self.wanted = wanted
		self.rsid = rsid

	def _dump(self, to_rs = True):
		return super()._dump('subreddit', 'rsid', to_rs=to_rs)

	def _load(rsid):
		rS = Result.get(rsid)
		if not rS:
			return None
		data = Task._load(rsid)
		sub = data.get('subreddit', None)
		length = rS.length - len(rS.results)
		if not sub is None and length  >=0:
			return Scan(sub, length, rsid)
		return None

	def _buildTask(self, subreddit, wanted, rsid):
		image_task = [GetLinks.s(subreddit),
						checkUrls.s(),
						update_results.s(rsid)]
		task = (GetSegments.s(subreddit) |
				to_chord.s(image_task, 
					check_results.s(rsid, subreddit))
				)
				# dchain.s(image_task) | 
				# check_results.s(rsid, sub/reddit))
		#  GetLinks.s(subreddit) |
		# 		to_chord.s(
		# 			checkUrls.s(),
		# 			update_results_set.s(rsid, wanted)))
				
		# task = (GetSegments.s(subreddit) |
		# 		to_chord.s(
		# 			GetLinks.s(subreddit)).clone(
		# 			args = (collapse_lists.s(),)) |
		# 		to_chord.s(
		# 			checkUrl.s()).clone(
		# 			args=(update_results_set.s(rsid, wanted),)))

		return task

	def _execute(self, subreddit, wanted, rsid):
		self._dump()
		task = self._buildTask(subreddit, wanted, rsid)
		task()
		return self.rsid

	def _before_task(self, *ar, **kw):
		return (self.subreddit, self.wanted, self.rsid), {}
