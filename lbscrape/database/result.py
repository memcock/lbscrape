from ..models import ResultSet
from .func import commit_record

class Result:
	@staticmethod
	def get(rsid):
		'''
			Return a ResultSet given its id or None
		'''
		return ResultSet.query.get(rsid)
		
	@staticmethod
	def create(length, *results):
		''' 
			Creates a ResultSet of length, optionaly adding results
		'''
		rS = ResultSet(length, *results)
		if commit_record(rS):
			return rS
		return None
	
	@staticmethod
	def add_to(rsid, results):
		'''
			Adds results to a ResultSet
		'''
		rS = Result.get(rsid)
		rS = Result.get(rsid)
		while results and len(rS.results) < rS.length:
			r = results.pop()
			rS.results.append(r)
		return commit_record(rS)
		