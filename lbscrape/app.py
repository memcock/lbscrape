from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from .config import config, getLogger
from celery import Celery

_log = getLogger(__name__)

app = Flask(config.meta.app)
dbUri = '%s%s:%s@%s'%(config.database.driver,
                        config.database.user, 
                        config.database.password,
                        config.database.path)
app.config['SQLALCHEMY_DATABASE_URI'] = dbUri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db = SQLAlchemy(app)

celery = Celery('task', broker = config.broker, backend = config.broker)


if __name__ == '__main__':
    app.run(debug=True)