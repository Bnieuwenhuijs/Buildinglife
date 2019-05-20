from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField, TextAreaField,SelectField, DecimalField, IntegerField, DateField
from wtforms.validators import DataRequired

class DashboardInputCharacteristicsForm(FlaskForm):
    building_year          = DateField(label='Building Year', format='%Y', validators=[DataRequired()])
    building_functionality = SelectField(label='Building Functionality', validators=[DataRequired()], choices=[("Residential", "Residential"), ("Office", "Office"), ("Other", "Other")])
    square_meters          = DecimalField(label="Square Meters", places=3, rounding=None)
    number_floors          = IntegerField(label="Number of Floors")

class DashboardIndividualInputMaterialForm(FlaskForm):
    material = DecimalField(places=3, rounding=None)

class DashboardInputMaterialsForm(FlaskForm):
    building_materials = FieldList(FormField(DashboardIndividualInputMaterialForm), min_entries=1)
