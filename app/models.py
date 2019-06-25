from app import db
from flask_login import UserMixin
from datetime import datetime
import hashlib, enum

class User(UserMixin, db.Model):
	__tablename__ = "user"

	id 						= db.Column(db.Integer, primary_key=True)
	name 					= db.Column(db.String(120))
	surname 				= db.Column(db.String(120))
	username 				= db.Column(db.String(64), index=True, unique=True)
	email 					= db.Column(db.String(120), index=True, unique=True)
	password_hash 			= db.Column(db.String(128))
	isConfirmed 			= db.Column(db.Boolean, default = False)

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Building(db.Model):
	__tablename__ = "Building"

	id                      = db.Column(db.Integer, primary_key=True)
	Street_name				= db.Column(db.String(120))
	Place_name				= db.Column(db.String(120))
	house_number 			= db.Column(db.String(120))
	postal_code				= db.Column(db.String(120))
	building_year           = db.Column(db.Integer)
	building_functionality  = db.Column(db.String(120))
	square_meters           = db.Column(db.Float)
	number_floors           = db.Column(db.Integer)
	ground_0_50				= db.Column(db.Integer)
	roof_0_25				= db.Column(db.Integer)
	roof_0_75				= db.Column(db.Integer)
	roof_0_95				= db.Column(db.Integer)
	roof_flat				= db.Column(db.Boolean, default = False)
	x_cordinate				= db.Column(db.String(120))
	y_cordinate				= db.Column(db.String(120))
	windows 				= db.Column(db.Integer)
	user_id                 = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Building {}>'.format(self.building_year)

class Material_estimation(db.Model):
	__tablename__ = "Material_estimation"

	id                      = db.Column(db.Integer, primary_key=True)
	total_value             = db.Column(db.Integer)
	steel_quantity          = db.Column(db.Integer)
	steel_Value             = db.Column(db.Integer)
	copper_quantity         = db.Column(db.Integer)
	copper_Value            = db.Column(db.Integer)
	concrete_quantity       = db.Column(db.Integer)
	concrete_Value          = db.Column(db.Integer)
	timber_quantity         = db.Column(db.Integer)
	timber_Value            = db.Column(db.Integer)
	glass_quantity          = db.Column(db.Integer)
	glass_Value             = db.Column(db.Integer)
	polystyrene_quantity    = db.Column(db.Integer)
	polystyrene_Value       = db.Column(db.Integer)
	building_id             = db.Column(db.Integer, db.ForeignKey('Building.id'))

	def __repr__(self):
		return '<Building {}>'.format(self.building_year)

class LicenseType(enum.Enum):
	STARTER		 = "Starter"
	PROFESSIONAL = "Pro"
	BUSINESS	 = "Business"


class License(UserMixin, db.Model):
	__tablename__ = 'license'

	id						= db.Column(db.Integer, primary_key=True)
	license_hash			= db.Column(db.String(128))
	user_id 				= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	end_date 				= db.Column(db.DateTime)
	license_type 			= db.Column(db.String(13))
	isActive				= db.Column(db.Boolean, default = False)

	def __init__(self, user_id, license_type, end_date = None):
		self.user_id 		= user_id
		self.end_date 		= end_date
		self.license_type 	= license_type
		self.isActive 		= True
		
		text = str(self.id) + str(datetime.now()) + str(self.license_type) + str(self.user_id)
		self.license_hash 	= hashlib.md5(text.encode("utf-8")).hexdigest()


	def __repr__(self):
		return '<User %r has bought license %s with id: %s>' % (self.user_id, self.id, self.license_hash) 




		