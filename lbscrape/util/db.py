
from sqlalchemy import inspect
from sqlalchemy.ext.declarative.clsregistry import _ModuleMarker
from sqlalchemy.orm import RelationshipProperty
import json

from hashids import Hashids
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
