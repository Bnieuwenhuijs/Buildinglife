from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, TextAreaField,SelectField, DecimalField, IntegerField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length

class DashboardInputCharacteristicsForm(FlaskForm):
    building_year          = DateField(label='Building Year', format='%Y', validators=[DataRequired()])
    building_functionality = SelectField(label='Building Functionality', validators=[DataRequired()], choices=[("Residential", "Residential"), ("Office", "Office"), ("Other", "Other")])
    square_meters          = DecimalField(label="Square Meters", validators=[DataRequired()], places=3, rounding=None)
    number_floors          = IntegerField(label="Number of Floors", validators=[DataRequired()])

class DashboardIndividualInputMaterialForm(FlaskForm):
    material = DecimalField(places=3, rounding=None)

class DashboardInputMaterialsForm(FlaskForm):
    building_materials = FieldList(FormField(DashboardIndividualInputMaterialForm), min_entries=1)

class RegisterForm(FlaskForm):
    email = StringField(label='email', validators=[DataRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField(label='username', validators=[DataRequired(), Length(min=4, max=15)])
    name = StringField(label='name', validators=[DataRequired()])
    surname = StringField(label='surname', validators=[DataRequired()])
    password = PasswordField(label='password', validators=[DataRequired(), Length(min=8, max=80)])

class LoginForm(FlaskForm):
    username = StringField(label='username', validators=[DataRequired(), Length(min=4, max=15)])
    password = PasswordField(label='password', validators=[DataRequired(), Length(min=8, max=80)])
    remember = BooleanField(label='remember me')
