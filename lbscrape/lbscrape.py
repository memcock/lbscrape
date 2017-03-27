import app as app
celery = app.celery
from .resource import Subreddit, Queue, Result, Check, Dummy200
from sqlalchemy.ext.declarative import declarative_base

# from .util.db import is_sane_database
# if not is_sane_database(declarative_base(), app.db.session):
#     app.db.create_all()
    
app.api.add_resource(Dummy200, '/')
app.api.add_resource(Subreddit, '/r/<subreddit>')
app.api.add_resource(Check, '/check/<subreddit>')
app.api.add_resource(Queue, '/queue/<rsid>')
app.api.add_resource(Result, '/result/<rsid>')

if __name__ == '__main__':
    app.celery.worker_main()