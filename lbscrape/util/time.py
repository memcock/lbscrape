from datetime import timedelta, datetime, timezone

def now():
	return datetime.utcnow()
	
def convert_delta(interval):
	'''
		Converts a timespan represented as a space seperated string 
		Xy Xd Xh Xm Xs to a datetime.timedelta object
		all segments are optional eg '2d 12h', '10m 30s', '1y 30s'
	'''
	seg_map = dict( h='hours',
					m='minutes',
					s='seconds',
					y='years',
					d='days')
	segs = interval.split(' ')
	kwargs = { seg_map[seg[-1]]: int(seg[:-1]) for seg in segs }
	return timedelta(**kwargs)

def utc_time(timestamp):
	'''
		converts a unix timestamp into a naive datetime object
	'''
	return datetime.fromtimestamp(float(timestamp))

def date(func):
	'''
		decarator to convert the return value of a function to a datetime object
	'''
	def inner(*args, **kwargs):
		timestamp = func(*args, **kwargs)
		return utc_time(float(timestamp)) if isinstance(timestamp, float) else None
	return inner

def max_delta(start, stop, delta):
	'''
		increments start by at most delta without passing stop
		eg	start 0 stop 10 delta 5 -> 5
			start 0 stop 10 delta 15 -> 10
	'''
	val = start  + delta
	if val > stop:
		return stop
	return val

def min_delta(start, stop, delta):
	'''
		decrements start by at most delta without passing stop
		eg	start 10 stop 0 delta 5 -> 5
			start 10 stop 5 delta 10 -> 0
	'''
	val = start - delta
	if val < stop:
		return stop
	return val
	
def iter_by_delta(start, stop, delta):
	'''
		yields (start, end) timestamps of at most delta length
		between the 2 given timestamps
		assumes utc, and returns naive datetime objects
		this function will always return timestamps moving "forward" in time 
		(past -> present) even if start > stop
	'''
	if not stop > start:
		start, stop = stop, start
	timestamp = start
	while timestamp < stop:
		timestamp = max_delta(timestamp, stop, delta)
		yield start, timestamp
		start = timestamp + timedelta(seconds = 1)