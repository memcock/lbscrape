from .reddit import GetLinks, GetSegments
from .util import to_chord, checkUrls, update_results_set
from ..database import create_result_set
 
class Task:
	def _execute(self, *args, **kwargs):
		pass 
	def __call__(self, *args, **kwargs):
		ar, kw = self._before_task(*args, **kwargs)
		return self._execute(*ar, **kw)


	def _before_task(self, *args, **kwargs):
		return args, kwargs
	
class Scan(Task):
	def __init__(self, subreddit, wanted, rsid):
		self._subreddit = subreddit
		self._wanted = wanted
		self._rsid = rsid

	def _buildTask(self, subreddit, wanted, rsid):
		task = (GetSegments.s(subreddit) | GetLinks.s(subreddit) |
				to_chord.s(
					checkUrls.s(),
					update_results_set.s(rsid, wanted)))
		return task

	def _execute(self, subreddit, wanted, rsid):
		task = self._buildTask(subreddit, wanted, rsid)
		task()
		return self._rsid

	def _before_task(self, *ar, **kw):
		return (self._subreddit, self._wanted, self._rsid), {}
