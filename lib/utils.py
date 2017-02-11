from datetime import timedelta, datetime, timezone
from collections import defaultdict
from hashids import Hashids
from sqlalchemy import inspect
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.orm import RelationshipProperty
import json

def is_sane_database(Base, session):
    """Check whether the current database matches the models declared in model base.

    Currently we check that all tables exist with all columns. What is not checked

    * Column types are not verified

    * Relationships are not verified at all (TODO)

    :param Base: Declarative Base for SQLAlchemy models to check

    :param session: SQLAlchemy session bound to an engine

    :return: True if all declared models have corresponding tables and columns.
    """

    engine = session.get_bind()
    iengine = inspect(engine)

    errors = False

    tables = iengine.get_table_names()

    # Go through all SQLAlchemy models
    for name, klass in Base._decl_class_registry.items():

        if isinstance(klass, _ModuleMarker):
            # Not a model
            continue

        table = klass.__tablename__
        if table in tables:
            # Check all columns are found
            # Looks like [{'default': "nextval('sanity_check_test_id_seq'::regclass)", 'autoincrement': True, 'nullable': False, 'type': INTEGER(), 'name': 'id'}]

            columns = [c["name"] for c in iengine.get_columns(table)]
            mapper = inspect(klass)

            for column_prop in mapper.attrs:
                if isinstance(column_prop, RelationshipProperty):
                    # TODO: Add sanity checks for relations
                    pass
                else:
                    for column in column_prop.columns:
                        # Assume normal flat column
                        if not column.key in columns:
                            logger.error("Model %s declares column %s which does not exist in database %s", klass, column.key, engine)
                            errors = True
        else:
            logger.error("Model %s declares table %s which does not exist in database %s", klass, table, engine)
            errors = True

    return not errors

def convert_delta(interval):
	'''
		Converts a timespan represented as a space seperated string 
		Xy Xd Xh Xm Xs 
		to a datetime.timedelta object
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
		converts a unix timestamp into a utc tz aware datetime object
	'''
	return datetime.fromtimestamp(float(timestamp))

def date(func):
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

def iter_by_delta(start, stop, delta):
	'''
		yields (start, end) timestamps of at most delta length
		between the 2 given timestamps
		assumes utc, and returns utc aware datetime objects
	'''
	if not stop > start:
		start, stop = stop, start
	timestamp = start
	while timestamp < stop:
		timestamp = max_delta(timestamp, stop, delta)
		yield start, timestamp
		start = timestamp + timedelta(seconds = 1)


def submission_to_dict(submission):
	'''
		Converts a reddit submission object into a dictionary
		to allow serialization so it can be sent over the wire
	'''
	data = dict(
		fullname = submission.fullname,
		created = submission.created_utc,
		subreddit = submission.subreddit.display_name
	)
	url = submission.preview['images'][0]['source']['url']
	data['url'] = url
	return data

hashids = Hashids(min_length=8)

def encode_id(id):
	'''
		Encodes numerical id as a unique short hash
	'''
	return hashids.encode(id)

def decode_id(id):
	'''
		Decodes unique short hashes into numerical ids
	'''
	return hashids.decode(id)

def collapse_double_list(dlist):
	'''
		collapses a list of lists	[[1,2,3],[4,5,6],[7,8,9]]
		into a single list 			[1,2,3,4,5,6,7,8,9]
	'''
	out = []
	for slist in dlist:
		if isinstance(slist, list):
			for v in slist:
				out.append(v)
		else:
			out.append(slist)
	return out

# Writes a submission to a json file
def log_submission(dir, submission):
	data = dict(
		fullname = submission.fullname,
		post_hint = getattr(submission, 'post_hint', None),
		url = getattr(submission, 'url', None),
		images = getattr(submission, 'preview', None)
	)

	with open(dir + '/%s.json'%submission.fullname, 'w') as f:
		json.dump(data, f)

