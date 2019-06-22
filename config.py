import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECURITY_PASSWORD_SALT = 'my_precious_two'
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		os.environ.get('DATABASE_URL_local')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

