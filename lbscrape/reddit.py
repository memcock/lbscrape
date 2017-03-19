from praw import Reddit
from prawcore.exceptions import Forbidden, NotFound, Redirect
import requests
from .config import config, getLogger
from .util import time

_log = getLogger(__name__)


def _build_client(**kwargs):
	defaults = dict(client_id = config.reddit.id,
					client_secret = config.reddit.secret,
					user_agent = config.reddit.user_agent
				)
	defaults.update(kwargs)
	_log.debug('building reddit client with %s'%defaults)
	return Reddit(**defaults)

_redditClient = _build_client()

def _create_subreddit_client(subreddit):
	return _redditClient.subreddit(subreddit)

def r(subreddit):
	'''
		returns a Subreddit praw abject for subreddit
	'''
	return _create_subreddit_client(subreddit)

def submissions(subreddit, start, end):
	'''
		Get submission from a subreddit between start and end timestamp
	'''
	client = r(subreddit)
	for submission in  client.submissions(start = start, end = end):
		yield submission

def images(*args, **kwargs):
	for submission in submissions(*args, **kwargs):
		# See if its an image submission
		if getattr(submission, 'post_hint', False) in ['image', 'link']: 
			# Make sure it has the images dict
			if getattr(submission, 'preview', False) and submission.preview.get('images', False):
				# yield only portrait images above 500x500 res
				width = submission.preview['images'][0]['source']['width']
				height = submission.preview['images'][0]['source']['height']
				if  height >= 500 and width >= 500 and height >= width:
					yield submission

def newest(subreddit):
	'''
		Get the newest submission from a subreddit
	'''
	client = r(subreddit)
	return [post for post in client.new(limit=1)][0]

def details(subreddit):
	'''
		Get some details about a subreddit
		returns a dict of values
		currently only returns the creation timestamp of the subreddit
	'''
	client = r(subreddit)
	data = {
		'created': time.utc_time(client.created_utc),
		'newest': time.utc_time(newest(subreddit).created_utc)
	}
	return data
	
def check(subreddit):
	'''
		Check if a subreddit exists and is public
	'''
	_log.debug('Checking if %s is a valid and public subreddit'%subreddit)
	sub = r(subreddit)
	try:
		sub.fullname
	except (NotFound, Redirect):
		_log.warning('%s is not a valid subreddit'%subreddit)
		return False
	except Forbidden:
		_log.warning('%s is a private subreddit'%subreddit)
		return False
	return True