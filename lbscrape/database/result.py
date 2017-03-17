from ..models import ResultSet
from .func import commit_record

class Result:
	@classmethod
	def get(cls, rsid):
		'''
			Return a ResultSet given its id or None
		'''
		return ResultSet.query.get(rsid)
		
	@classmethod
	def create(cls, length, results = []):
		''' 
			Creates a ResultSet of length, optionaly adding results
		'''
		rS = ResultSet(length, *results)
		if commit_record(rS):
			return rS
		return None
	
	@classmethod
	def add_to(cls, rsid, results):
		'''
			Adds results to a ResultSet
		'''
		rS = Result.get(rsid)
		for result in results:
			rS.results.append(result)
		commit_record(result)
