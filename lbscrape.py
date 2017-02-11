import app 
celery = app.celery
from lib.resource import Subreddit, Queue, Result, Check
from sqlalchemy.ext.declarative import declarative_base
import lib.utils as utils

# if not utils.is_sane_database(declarative_base(), app.db.session):
#     app.db.create_all()
    
app.api.add_resource(Subreddit, '/r/<subreddit>')
app.api.add_resource(Check, '/check/<subreddit>')
app.api.add_resource(Queue, '/queue/<job_id>')
app.api.add_resource(Result, '/result/<job_id>')

if __name__ == '__main__':
    app.celery.worker_main()