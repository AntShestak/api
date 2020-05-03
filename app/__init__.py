from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

api = Flask(__name__)
api.config["DEBUG"] = True
api.config.from_object(Config)

db = SQLAlchemy(api)
migrate = Migrate(api, db)


from app import routes, models



