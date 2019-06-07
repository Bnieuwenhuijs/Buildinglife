from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, TextAreaField,SelectField, DecimalField, IntegerField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class DashboardInputCharacteristicsForm(FlaskForm):
	building_year			= DateField(label='Building Year', format='%Y', validators=[DataRequired()])
	building_functionality	= SelectField(label='Building Functionality', validators=[DataRequired()], choices=[("Residential", "Residential"), ("Office", "Office"), ("Other", "Other")])
	square_meters			= DecimalField(label="Square Meters", validators=[DataRequired()], places=3, rounding=None)
	number_floors			= IntegerField(label="Number of Floors", validators=[DataRequired()])

class DashboardIndividualInputMaterialForm(FlaskForm):
	material = DecimalField(places=3, rounding=None)

class DashboardInputMaterialsForm(FlaskForm):
	building_materials = FieldList(FormField(DashboardIndividualInputMaterialForm), min_entries=1)

class RegisterForm(FlaskForm):
	email 		= StringField(label='email', validators=[DataRequired(), Email(message='Invalid email'), Length(max=50)])
	username 	= StringField(label='username', validators=[DataRequired()])
	name 		= StringField(label='name', validators=[DataRequired()])
	surname 	= StringField(label='surname', validators=[DataRequired()])
	password 	= PasswordField(label='password', validators=[DataRequired()])

class LoginForm(FlaskForm):
	username 	= StringField(label='username', validators=[DataRequired()])
	password 	= PasswordField(label='password', validators=[DataRequired()])
	remember 	= BooleanField(label='remember me')

class EditUserProfileForm(FlaskForm):
	user_display_name 		= StringField(label='Display user name')
	user_display_surname	= StringField(label='Display user surname')
	user_display_username	= StringField(label='Display user username')

class EditUserEmailForm(FlaskForm):
	user_main_email 			= StringField(label='email', validators=[DataRequired(), Email(message='Invalid email'), Length(max=50)])
	user_main_email_newsletter 	= SelectField(label='Newsletter options', validators=[DataRequired()], choices=[("Yes", "Yes"), ("No", "No")])

