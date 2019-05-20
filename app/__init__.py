from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bcvuhfokdvquhx:dd1f665b71b0fb8fd677412383da95856fbb5cd3a2c10716ff5aa2b1fb0ba98a@ec2-23-23-228-132.compute-1.amazonaws.com:5432/damf0i63c60khm'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes