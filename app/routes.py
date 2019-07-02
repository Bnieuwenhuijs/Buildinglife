#!flask/bin/python

from flask import render_template, jsonify
from flask import request, flash, redirect, url_for

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from app import app
from app import db
from app.models import Building, User, License, Material_estimation
from app.forms import DashboardInputCharacteristicsForm, DashboardIndividualInputMaterialForm, DashboardInputMaterialsForm, RegisterForm, LoginForm, BuildingManagementForm, EditUserProfileForm, DeleteUserProfileForm, UpdateUserLicenseForm, BuyStarterLicenseForm, BuyProfessionalLicenseForm, BuyBusinessLicenseForm
from app.forms import EditUserProfileForm, DeleteUserProfileForm, UpdateUserLicenseForm, BuyStarterLicenseForm, BuyProfessionalLicenseForm, BuyBusinessLicenseForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pathlib import Path
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from urllib.request import urlopen
from app.Building_information_api import get_building_properties
from validate_email import validate_email
from app.email_templates import generate_html_mail, welcome_email_body

from datetime import timedelta
from datetime import datetime
import os, pickle, requests, json, datetime, smtplib, ssl


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

MAIL_SERVER='mail.buildinglife.nl'
MAIL_PORT= 465
MAIL_USERNAME= 'no-reply@buildinglife.nl'
MAIL_PASSWORD= 'test'


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

def value_calculation(KG, price, depreciation_rate, diminishing_value_rate, recyclability, years_old):
	#mult_KG_price = KG * price

	if price * ( depreciation_rate * years_old) < price * (1-recyclability):
		price_per_kg = price * 0.1
	else:
		price_per_kg = price * (depreciation_rate * years_old)

	diminish_value = (3 * diminishing_value_rate) * price_per_kg

	recyclability  = price * recyclability

	estimated_value = (float(price_per_kg) * float(KG)) - diminish_value + recyclability

	return estimated_value

def quantity_value_estimation(square_meters, building_year, ground_0_50, roof_0_25, roof_0_75, roof_0_95, functionality, roof_flat_bool, windows, Steel = 0, Copper = 0, Concrete = 0, Timber = 0, Glass = 0, Polystyrene = 0):

	# Convert the type of roof to a number for the model
	if roof_flat_bool == False :
		roof_flat = 0
	else:
		roof_flat = 1

	# Convert the functionality to a number for the model
	if functionality.lower() == "woonfunctie":
		building_func = 1
	elif functionality.lower() == "winkelfunctie":
		building_func = 2
	elif functionality.lower() == "industriefunctie":
		building_func = 3
	else:
		building_func = 4

	## Load all the models
	regression_model_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "regression_models")

	age = datetime.datetime.now().year - building_year

	if windows == 0:
		steel_model = pickle.load(open(os.path.join(regression_model_path, "steel_model.sav"), 'rb'))
		concrete_model = pickle.load(open(os.path.join(regression_model_path, "concrete_model.sav"), 'rb'))
		copper_model = pickle.load(open(os.path.join(regression_model_path, "copper_model.sav") , 'rb'))
		glass_model = pickle.load(open(os.path.join(regression_model_path, "glass_model.sav"), 'rb'))
		polystyrene_model = pickle.load(open(os.path.join(regression_model_path, "polystyrene_model.sav"), 'rb'))
		timber_model = pickle.load(open(os.path.join(regression_model_path, "timber_model.sav"), 'rb'))

		print("ESTIMATION HIER")
		print(Steel)
		print(Concrete)

		if Steel == 0 or Steel == None or Steel == "None":
			Steel = abs(steel_model.predict([[age,building_func,(roof_0_75 - ground_0_50), (roof_0_95 - ground_0_50), roof_flat, round((roof_0_95 - ground_0_50) / 3)]])[0])
			Steel *= square_meters
		
		print("ESTIMATION HIER2")
		print(Steel)

		if Concrete == 0 or Concrete == None:
			Concrete = abs(concrete_model.predict([[age,building_func,(roof_0_75 - ground_0_50), (roof_0_95 - ground_0_50), roof_flat, round((roof_0_95 - ground_0_50) / 3)]])[0])
			Concrete *= square_meters
		if Copper == 0 or Copper == None:
			Copper = abs(copper_model.predict([[age,building_func,(roof_0_75 - ground_0_50), (roof_0_95 - ground_0_50), roof_flat, round((roof_0_95 - ground_0_50) / 3)]])[0])
			Copper *= square_meters
		if Glass == 0 or Glass == None:
			Glass = abs(glass_model.predict([[age,building_func,(roof_0_75 - ground_0_50), (roof_0_95 - ground_0_50), roof_flat, round((roof_0_95 - ground_0_50) / 3)]])[0])
			Glass *= square_meters
		if Polystyrene == 0 or Polystyrene == None:	
			Polystyrene = abs(polystyrene_model.predict([[age,building_func,(roof_0_75 - ground_0_50), (roof_0_95 - ground_0_50), roof_flat, round((roof_0_95 - ground_0_50) / 3)]])[0])
			Polystyrene *= square_meters
		if Timber == 0 or Timber == None:
			Timber = abs(timber_model.predict([[age,building_func,(roof_0_75 - ground_0_50), (roof_0_95 - ground_0_50), roof_flat, round((roof_0_95 - ground_0_50) / 3)]])[0])			
			Timber *= square_meters

	if windows > 0:
		steel_window_model = pickle.load(open(os.path.join(regression_model_path, "steel_window_model.sav"), 'rb'))
		copper_window_model = pickle.load(open(os.path.join(regression_model_path, "copper_window_model.sav"), 'rb'))
		timber_window_model = pickle.load(open(os.path.join(regression_model_path, "timber_window_model.sav"), 'rb'))
		concrete_window_model = pickle.load(open(os.path.join(regression_model_path, "concrete_window_model.sav"), 'rb'))
		glass_window_model = pickle.load(open(os.path.join(regression_model_path, "glass_window_model.sav"), 'rb'))
		concrete_window_model = pickle.load(open(os.path.join(regression_model_path, "copper_window_model.sav"), 'rb'))
		polystyrene_window_model = pickle.load(open(os.path.join(regression_model_path, "polystyrene_window_model.sav"), 'rb'))

		if Steel == 0 or Steel == None:
			Steel = abs(steel_window_model.predict([[age,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
			Steel *= square_meters
		if Concrete == 0 or Concrete == None:
			Concrete = abs(concrete_window_model.predict([[age,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
			Concrete *= square_meters
		if Copper == 0 or Copper == None:
			Copper = abs(copper_window_model.predict([[age,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
			Copper *= square_meters
		if Glass == 0 or Glass == None:
			Glass = abs(glass_window_model.predict([[age,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
			Glass *= square_meters
		if Polystyrene == 0 or Polystyrene == None:
			Polystyrene = abs(polystyrene_window_model.predict([[age,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
			Polystyrene *= square_meters
		if Timber == 0 or Timber == None:
			Timber = abs(timber_window_model.predict([[age,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])			
			Timber *= square_meters

	#Value_estimations
	steel_value       = value_calculation(float(Steel), 2.15, 0.066, 0.1333, 0.86, (datetime.datetime.now().year - building_year ) )
	copper_value      = value_calculation(float(Copper), 3.56, 0.05, 0.1, 1, (datetime.datetime.now().year - building_year ) )
	concrete_value    = value_calculation(float(Concrete), 1, 0.02, 0.04, 0.8, (datetime.datetime.now().year - building_year ) )
	timber_value      = value_calculation(float(Timber), 0.85, 0.2, 0.4, 0.66, (datetime.datetime.now().year - building_year ) )
	glass_value       = value_calculation(float(Glass), 1.15, 0.0667, 0.13, 1, (datetime.datetime.now().year - building_year ) )
	polystyrene_value = value_calculation(float(Polystyrene), 0.75, 0.1, 0.2, 0.87, (datetime.datetime.now().year - building_year ) )
		
	total_list = [steel_value, copper_value, concrete_value, timber_value, glass_value, polystyrene_value]
	total_value = sum(total_list)

	return_dictionary = { 'steel_quantity' : Steel, 'copper_quantity' : Copper, 'concrete_quantity' : Concrete, 'timber_quantity' : Timber,
						  'timber_quantity' : Timber, 'glass_quantity' : Glass, 'polystyrene_quantity' : Polystyrene,
						  'steel_value' : steel_value, 'copper_value' : copper_value, 'concrete_value' : concrete_value, 'timber_value' : timber_value,
						  'glass_value' : glass_value, 'polystyrene_value' : polystyrene_value, 'total_value' : total_value}

	return return_dictionary

# Functions for the index.
# The index.... functions relate to going to a specific section on the website
@app.route('/')
@app.route('/index')
def index():
	user = {'username': 'Miguel'}
	return render_template('index.html')

@app.route('/indexabout')
def indexabout():
	return render_template('index.html', scroll='about')

@app.route('/indexservices')
def indexservices():
	return render_template('index.html', scroll='services')

@app.route('/indexteam')
def indexteam():
	return render_template('index.html', scroll='team')

@app.route('/indexcontact')
def indexcontact():
	return render_template('index.html', scroll='contact')

@app.route('/login', methods=['GET', 'POST'])
def login():

	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if not user.isConfirmed:
				return render_template('unconfirmed_user.html', name=user.name)
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))
		else:
			if not user:
				flash('Your login/password does not match or exists', 'alert alert-danger')
			elif not user.isConfirmed:
				flash('Your account is not confirmed yet. Check your email', 'alert alert-danger')

		#return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

	return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

	form = RegisterForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if not user:
			user1 = User.query.filter_by(email=form.email.data).first()
			if not user1:
				hashed_password = generate_password_hash(form.password.data, method='sha256')
				new_user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password, name=form.name.data, surname=form.surname.data)
				
				# Send the confirmation email
				# Generate a confirmation token
				token = s.dumps(form.email.data, salt = 'email-confirm')

				link = url_for('confirm_email', token = token, _external = True)

				server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
				server.login(MAIL_USERNAME, MAIL_PASSWORD)

				user_full_name = form.name.data + " " + form.surname.data

				email = generate_html_mail("Welcome to BuildingLife!", 
					welcome_email_body(user_full_name, link),
					form.email.data,
					MAIL_USERNAME)

				'''
				if not validate_email(form.email.data, verify = True):
					flash('Please use a valid email', 'alert alert-danger')
					return render_template('signup.html', form = form)
				'''

				server.sendmail(MAIL_USERNAME, form.email.data, email)
				server.quit() 

				db.session.add(new_user)
				db.session.commit()
				flash('You successfully created your account. Check your email to confirm it.', 'alert alert-success')
			else:
				flash('There is already an account with that email', 'alert alert-danger')
		else:
			flash('There is already an account with that username', 'alert alert-danger')
	return render_template('signup.html', form=form)

@app.route('/confirm_email')
@app.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
	try:
		# 60*15, the link is active for 15 minutes
		email = s.loads(token, salt = 'email-confirm')
		user = User.query.filter_by(email=email).first()
		user.isConfirmed = True
		db.session.add(user)
		db.session.commit()

		return render_template('confirmed_user.html', name = user.name)
	except SignatureExpired:
		return '<h1>Token expired </h1>'
	except BadTimeSignature:
		return render_template('token_non_existing.html')

@app.route('/confirmed_user', methods=['GET', 'POST'])
def confirmed_user():
	return render_template('confirmed_user.html', name = None)

@app.route('/unconfirmed_user', methods=['GET', 'POST'])
def unconfirmed_user():
	return render_template('unconfirmed_user.html', name = None)

@app.route('/token_expired', methods=['GET', 'POST'])
def token_expired():
	return render_template('token_expired.html', user = None)

@app.route('/token_non_existing', methods=['GET', 'POST'])
def token_non_existing():
	return render_template('token_non_existing.html')

@app.route('/dashboard')
def dashboard():
	form_building_charachteristics = DashboardInputCharacteristicsForm()
	return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0, name=current_user.username, tryout = False)

@app.route('/try')
def trydashboard():
	form_building_charachteristics = DashboardInputCharacteristicsForm()
	return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0, tryout = True)

@app.route('/dashboard', methods=['GET', 'POST'])
def testing():

	if request.method=='POST':

		tryout = request.args.get('tryout', None)[0] == "T"
		print(tryout)

		# WTform for the building characteristics input
		form_building_charachteristics = DashboardInputCharacteristicsForm()

		# Get the location information
		postalcode = form_building_charachteristics.postalcode.data
		city = form_building_charachteristics.city.data
		housenumber = form_building_charachteristics.housenumber.data
		streetname = form_building_charachteristics.streetname.data

		# Get if the amount of windows should be taken into account
		windowchecked = request.form.get("windowcount") != None

		# Get the cordinates
		gebruiksdoel_Oppervlakte_data = requests.get('http://geodata.nationaalgeoregister.nl/locatieserver/free?rows=1&&fq=postcode:' + postalcode + '&&fq=huisnummer:' + housenumber + '&&fq=type:adres'
		).json()

		if list(gebruiksdoel_Oppervlakte_data.keys())[0] == 'error':
			form_building_charachteristics = DashboardInputCharacteristicsForm()
			flash("The provided information is incorrect or the building does not exist.", 'alert alert-danger')

			return render_template("dashboard.html", form_build_char=form_building_charachteristics, numberOfMaterialsDisplayed = 0) # name=current_user.username, 
		
		response = gebruiksdoel_Oppervlakte_data["response"]

		# Check if a valid building has been provided
		if (response["numFound"] == 0):
			# Flash here
			flash("The provided information is incorrect or the building does not exist.", 'alert alert-danger')
			form_building_charachteristics = DashboardInputCharacteristicsForm()
			return render_template("dashboard.html", form_build_char=form_building_charachteristics, numberOfMaterialsDisplayed = 0, tryout=tryout) # name=current_user.username, 
		
		# Get the cordinates in the format (Point(Y-cordinate, X-cordinate))
		cordinates = response['docs'][0]['centroide_ll']

		x_cordinate = cordinates[int(cordinates.index(' ')) + 1 : int(cordinates.index(')'))]
		y_cordinate = cordinates[int(cordinates.index('(')) + 1 : int(cordinates.index(' '))]
		cordinates = x_cordinate + "," + y_cordinate

		# Get the building properties
		building_properties = get_building_properties(postalcode, 
										housenumber, 
										windowchecked)

		# Get some properties to add to the database
		building_year = building_properties['Building_year']
		building_functionality = building_properties['building_functionality']
		square_meters = building_properties['square_meters']
		ground_0_50 = building_properties['ground_0_50']
		roof_0_25 = building_properties['roof_0_25']
		roof_0_75 = building_properties['roof_0_75']
		roof_0_95 = building_properties['roof_0_95']
		roof_flat = building_properties['roof_flat']
		number_floors = round((roof_0_95 - ground_0_50) / 3)

		windows = 0
		if windowchecked:
			windows = building_properties['windows']

		# Add to the database
		building = Building(Street_name = streetname, Place_name = city, building_year = building_year, postal_code	= postalcode, building_functionality = building_functionality,
							square_meters = square_meters, ground_0_50 = ground_0_50, roof_0_25 = roof_0_25, roof_0_75 = roof_0_75,
							roof_0_95 = roof_0_95, x_cordinate = x_cordinate, y_cordinate = y_cordinate, user_id = 1, #current_user.id, 
							number_floors = number_floors, house_number = housenumber, windows = windows, roof_flat = roof_flat )
							
		db.session.add(building)
		db.session.commit()

		database_id = building.id

		# Extract the values of the materials.
		# If not provided, returns null
		Steel       = request.form.get("Steel_input")
		Copper      = request.form.get("Copper_input")
		Concrete    = request.form.get("Concrete_input")
		Timber      = request.form.get("Timber_input")
		Glass       = request.form.get("Glass_input")
		Polystyrene = request.form.get("Polystyrene_input")

		# Create an estimation to fill 
		material_estimation = Material_estimation( total_value = None, 
												   steel_quantity = Steel, steel_Value = None, 
												   copper_quantity = Copper, copper_Value = None,
												   concrete_quantity = Concrete, concrete_Value = None,
												   timber_quantity = Timber, timber_Value = None,
												   glass_quantity = Glass, glass_Value = None,
												   polystyrene_quantity = Polystyrene, polystyrene_Value = None,
												   building_id = database_id )
		db.session.add(material_estimation)
		db.session.commit()

		building_Information = Building.query.filter(Building.id == database_id)
		database_ids = [database_id]

		return render_template("parameters.html", 
								building_Information = building_Information, 
								database_ids = database_ids, 
								windowchecked = windowchecked,
								material_estimation_id = material_estimation.id,
								buildingManagement = False,
								tryout=tryout)

@app.route('/history')
def history():
	material_estimation =  Material_estimation.query.order_by(Material_estimation.building_id.desc())

	material_estimation_dict = []

	for mat_est in material_estimation:
		material_estimation_dict.append({"Steel_value" : mat_est.steel_Value,
		                                 "Steel_quantity" : mat_est.steel_quantity,
										 "Concrete_value" : mat_est.concrete_Value,
										 "Concrete_quantity" : mat_est.concrete_quantity,
										 "Copper_value" : mat_est.copper_Value,
										 "Copper_quantity" : mat_est.copper_quantity,
										 "Glass_value" : mat_est.glass_Value,
										 "Glass_quantity" : mat_est.glass_quantity,
										 "Timber_value" : mat_est.timber_Value,
										 "Timber_quantity" : mat_est.timber_quantity,
										 "Polystyrene_value" : mat_est.polystyrene_Value,
										 "Polystyrene_quantity" : mat_est.polystyrene_quantity,
										 "Total_value" : mat_est.total_value})


	buildings = Building.query.order_by(Building.id.desc())

	size = len(material_estimation_dict)

	return render_template('history.html', buildings=buildings, material_estimation_dict = material_estimation_dict, size = size)

@app.route('/BuildingManagement')
def BuildingManagement():

	BMform = BuildingManagementForm()

	headers = {'Content-Type': 'application/json'}
	response = requests.get('http://geodata.nationaalgeoregister.nl/locatieserver/free?fq=postcode:3452AM', headers=headers)

	#if response.status_code == 200:
		#print (json.loads(response.content.decode('utf-8')) )
	#else:
	#	print("Got an error")

	return render_template('buildingmanagement.html', BuildingManagementForm = BMform)

@app.route('/UserProfile', methods=['GET', 'POST'])
@login_required
def UserProfile():
	update_user_license_form = UpdateUserLicenseForm()
	license = License.query.filter(License.user_id == User.id).first()
	
	'''
	if update_user_license_form.validate_on_submit():
		license = License.query.filter(License.user_id == User.id).first()
	elif request.method == 'GET':
		update_user_license_form.bought_at.data 		= license.start_date
		update_user_license_form.expires.data 			= license.end_date
		update_user_license_form.id 					= license.id
	'''

	edit_user_profile_form = EditUserProfileForm()

	if edit_user_profile_form.validate_on_submit():
		current_user.username 	= edit_user_profile_form.user_display_username.data
		current_user.name 		= edit_user_profile_form.user_display_name.data
		current_user.surname 	= edit_user_profile_form.user_display_surname.data
		current_user.email 		= edit_user_profile_form.user_display_email.data
		db.session.commit()
		# Something's fishy with this... DO NOT UNCOMMENT
		# flash('Your account has been updated!', 'success')

		return redirect(url_for('UserProfile'))

	elif request.method == 'GET':
		edit_user_profile_form.user_display_username.data 	= current_user.username
		edit_user_profile_form.user_display_name.data 		= current_user.name
		edit_user_profile_form.user_display_surname.data 	= current_user.surname
		edit_user_profile_form.user_display_email.data 		= current_user.email


	delete_user_profile_form = DeleteUserProfileForm()
	if delete_user_profile_form.validate_on_submit():
		#the_currently_connected_user = current_user
		User.query.filter(User.username == current_user.username).delete()
		db.session.commit()
		# Something's fishy with this... DO NOT UNCOMMENT
		# flash('Your account has been updated!', 'success')
		return redirect(url_for('index'))

	user = User.query.filter_by(username=current_user.username).first_or_404()
	return render_template('userprofile.html',
		user = user,
		edit_user_profile_form = edit_user_profile_form,
		delete_user_profile_form = delete_user_profile_form,
		license = license,
		update_user_license_form = update_user_license_form)


@app.route('/purchase', methods=['GET', 'POST'])
@login_required
def purchase():
	buy_starter_form 		= BuyStarterLicenseForm()
	buy_professional_form 	= BuyProfessionalLicenseForm()
	buy_business_form 		= BuyBusinessLicenseForm()

	new_license = None

	if buy_starter_form.validate_on_submit():
		new_license = License(user_id = current_user.id, 
					  license_type = 'Starter',
					  end_date = datetime.datetime.now() + timedelta(days=365),
					  )

		db.session.add(new_license)
		db.session.commit()

		return redirect(url_for('UserProfile'))

	if buy_professional_form.validate_on_submit():
		new_license = License(user_id = current_user.id, 
					  license_type = 'Professional',
					  end_date = datetime.datetime.now() + timedelta(days=365),
					  )

		db.session.add(new_license)
		db.session.commit()

		return redirect(url_for('UserProfile'))

	if buy_business_form.validate_on_submit():
		new_license = License(user_id = current_user.id, 
					  license_type = 'Business',
					  end_date = datetime.datetime.now() + timedelta(days=365),
					  )

		db.session.add(new_license)
		db.session.commit()

		return redirect(url_for('UserProfile'))

	return render_template('purchase.html',
		license = license,
		buy_starter_form = buy_starter_form, 
		buy_professional_form = buy_professional_form, 
		buy_business_form = buy_business_form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route('/suppr', methods=['GET', 'POST'])
def suppr():
	idEstimation = request.args.get('idEstimation', None)
	Building.query.filter(Building.id == idEstimation).delete()
	db.session.commit()
	buildings = Building.query.order_by(Building.id.desc())
	return redirect(url_for('history'))
	
@app.route('/postlocationdata', methods = ['POST', 'GET'])
def get_post_location_data():

	buildingList = request.form['buildingList']

	windowchecked = request.form['window_checked_data'][0] == "t"
	
	#buildingList = json.loads(jsdata)

	return jsonify(windowchecked = windowchecked,
				   buildingList = buildingList)

@app.route('/parameters' )
def parameters():

	wchecked = request.args.get('windowchecked')[0] == "t"

	buildingList = request.args.get('buildingList')
	buildingList = json.loads(buildingList)

	database_ids = []
	building_Information_list = []

	# For each building in the list get the building characteric information
	for building in buildingList:
		streetname = building[1]
		postalcode = building[2]
		housenumber = building[3]
		city = building[4]

		cordinates = building[0]

		x_cordinate = cordinates[0 : int(cordinates.index(','))]
		y_cordinate = cordinates[int(cordinates.index(',')) + 1 : len(cordinates)]
		
		building_properties = get_building_properties(postalcode, housenumber, window_count = wchecked)

		building_year = building_properties['Building_year']
		building_functionality = building_properties['building_functionality']
		square_meters = building_properties['square_meters']
		ground_0_50 = building_properties['ground_0_50']
		roof_0_25 = building_properties['roof_0_25']
		roof_0_75 = building_properties['roof_0_75']
		roof_0_95 = building_properties['roof_0_95']
		roof_flat = building_properties['roof_flat']
		number_floors = round((roof_0_95 - ground_0_50) / 3)
		
		windows = 0
		if wchecked:
			windows = building_properties['windows']


		# Add to the database
		building = Building(Street_name = streetname, Place_name = city, building_year = building_year,
							building_functionality = building_functionality, postal_code = postalcode, square_meters = square_meters, 
							ground_0_50 = ground_0_50, roof_0_25 = roof_0_25, roof_0_75 = roof_0_75, roof_0_95 = roof_0_95, 
							x_cordinate = x_cordinate, y_cordinate = y_cordinate, user_id = 1,  number_floors = number_floors, 
							house_number = housenumber, windows = windows, roof_flat = roof_flat )
							
		db.session.add(building)
		db.session.commit()
		
		database_id = building.id
		database_ids.append(database_id)
		
		building_Information_list.append(Building.query.filter(Building.id == database_id).first())

	return render_template("parameters.html", 
							building_Information = building_Information_list, 
							database_ids = database_ids, 
							windowchecked = wchecked,
							buildingManagement = True)

@app.route('/building_management_estimation')
def building_management_estimation():

	database_ids = json.loads(request.args.get('database_ids', None))

	windowchecked = request.args.get('windowchecked', None)
	buildingManagement =  request.args.get('buildingManagement', None)

	# Create list to store values in
	material_value_dict = []

	total_steel_value = 0
	total_copper_value = 0
	total_timber_value = 0
	total_concrete_value = 0
	total_glass_value = 0
	total_polystyrene_value = 0

	total_steel_quantity = 0
	total_copper_quantity = 0
	total_timber_quantity = 0
	total_concrete_quantity = 0
	total_glass_quantity = 0
	total_polystyrene_quantity = 0

	if buildingManagement[0] == 'F':
		tryout = request.args.get('tryout', None)[0] == "T"
		material_estimation_id =  request.args.get('material_estimation_id')

		# TO FIC: GET THE GLOBAL VARIABLES
		# Get the database row for the estimation in question
		building = Building.query.get(int(database_ids[0]))

		# Get the building characteristics
		square_meters = building.square_meters
		building_year = building.building_year
		ground_0_50 = building.ground_0_50
		roof_0_25 = building.roof_0_25
		roof_0_75 = building.roof_0_75
		roof_0_95 = building.roof_0_95
		functionality = building.building_functionality
		roof_flat_bool = building.roof_flat
		windows = building.windows
		nr_floors = building.number_floors
		
		known_quantity_material = Material_estimation.query.get(int(material_estimation_id))

		quantity_value_dict = quantity_value_estimation(square_meters, 
														building_year, 
														ground_0_50, 
														roof_0_25, 
														roof_0_75, 
														roof_0_95, 
														functionality, 
														roof_flat_bool, 
														windows,
														Steel = known_quantity_material.steel_quantity,
														Copper = known_quantity_material.copper_quantity,
														Concrete = known_quantity_material.concrete_quantity,
														Timber = known_quantity_material.timber_quantity,
														Glass = known_quantity_material.glass_quantity,
														Polystyrene = known_quantity_material.polystyrene_quantity)

		#Put in DB
		material_estimation = Material_estimation.query.filter_by(building_id  = database_ids[0]).first()
		material_estimation = Material_estimation( total_value = quantity_value_dict['total_value'], 
												   steel_quantity = quantity_value_dict['steel_quantity'], steel_Value = quantity_value_dict['steel_value'], 
												   copper_quantity = quantity_value_dict['copper_quantity'], copper_Value = quantity_value_dict['copper_value'],
												   concrete_quantity = quantity_value_dict['concrete_quantity'], concrete_Value = quantity_value_dict['concrete_value'],
												   timber_quantity = quantity_value_dict['timber_quantity'], timber_Value = quantity_value_dict['timber_value'],
												   glass_quantity = quantity_value_dict['glass_quantity'], glass_Value = quantity_value_dict['glass_value'],
												   polystyrene_quantity = quantity_value_dict['polystyrene_quantity'], polystyrene_Value = quantity_value_dict['polystyrene_value'],
												   building_id = database_ids[0] )
							
		db.session.add(material_estimation)
		db.session.commit()

		material_value_dict =  [{ "Name" : "Steel", "Quantity" : round(float(quantity_value_dict['steel_quantity']),2), "Value" : round(float(quantity_value_dict['steel_value']),2)},
                                { "Name" : "Copper", "Quantity" : round(float(quantity_value_dict['copper_quantity']),2), "Value" : round(float(quantity_value_dict['copper_value']),2)},
                                { "Name" : "Concrete", "Quantity" : round(float(quantity_value_dict['concrete_quantity']),2), "Value" : round(float(quantity_value_dict['concrete_value']),2)},
                                { "Name" : "Timber", "Quantity" : round(float(quantity_value_dict['timber_quantity']),2), "Value" : round(float(quantity_value_dict['timber_value']),2)},
                                { "Name" : "Glass", "Quantity" : round(float(quantity_value_dict['glass_quantity']),2), "Value" : round(float(quantity_value_dict['glass_value']),2)},
                                { "Name" : "Polystyrene", "Quantity" : round(float(quantity_value_dict['polystyrene_quantity']),2), "Value" : round(float(quantity_value_dict['polystyrene_value']),2)}]


		return render_template('estimation.html',
                               total_value = quantity_value_dict['total_value'],
                               material_value_dict = material_value_dict,
                               building_year = building_year,
                               functionality = functionality,
                               square_meters = square_meters,
                               number_floors = nr_floors,
							   dashboard_used = True,
							   tryout = tryout
                               )


		

	elif buildingManagement[0] == "T":
		building_list_db = []
		estimation_list_db = []
		total_value = 0


		for database_id in database_ids:
			building = Building.query.filter_by(id = database_id).first()
			building_list_db.append(building)

			# Get the building characteristics
			square_meters = building.square_meters
			building_year = building.building_year
			ground_0_50 = building.ground_0_50
			roof_0_25 = building.roof_0_25
			roof_0_75 = building.roof_0_75
			roof_0_95 = building.roof_0_95
			functionality = building.building_functionality
			roof_flat_bool = building.roof_flat
			windows = building.windows
			nr_floors = building.number_floors

			quantity_value_dict = quantity_value_estimation(square_meters, 
														building_year, 
														ground_0_50, 
														roof_0_25, 
														roof_0_75, 
														roof_0_95, 
														functionality, 
														roof_flat_bool, 
														windows)
		
			# Put in DB
			material_estimation = Material_estimation( total_value = quantity_value_dict['total_value'], 
												  	 steel_quantity = quantity_value_dict['steel_quantity'], steel_Value = quantity_value_dict['steel_value'], 
												   	copper_quantity = quantity_value_dict['copper_quantity'], copper_Value = quantity_value_dict['copper_value'],
												   	concrete_quantity = quantity_value_dict['concrete_quantity'], concrete_Value = quantity_value_dict['concrete_value'],
												   	timber_quantity = quantity_value_dict['timber_quantity'], timber_Value = quantity_value_dict['timber_value'],
												   	glass_quantity = quantity_value_dict['glass_quantity'], glass_Value = quantity_value_dict['glass_value'],
												   	polystyrene_quantity = quantity_value_dict['polystyrene_quantity'], polystyrene_Value = quantity_value_dict['polystyrene_value'],
												   	building_id = database_ids[0] )
							
			db.session.add(material_estimation)
			db.session.commit()

			estimation_list_db.append(Material_estimation.query.filter_by(id = int(material_estimation.id)).first())

			steel_quantity = round(float(quantity_value_dict['steel_quantity']),2)
			copper_quantity  = round(float(quantity_value_dict['copper_quantity']),2)
			concrete_quantity = round(float(quantity_value_dict['copper_quantity']),2)
			timber_quantity = round(float(quantity_value_dict['timber_quantity']),2)
			glass_quantity = round(float(quantity_value_dict['glass_quantity']),2)
			polystyrene_quantity = round(float(quantity_value_dict['polystyrene_quantity']),2)

			steel_value = round(float(quantity_value_dict['steel_value']),2)
			copper_value = round(float(quantity_value_dict['copper_value']),2)
			concrete_value = round(float(quantity_value_dict['concrete_value']),2)
			timber_value = round(float(quantity_value_dict['timber_value']),2)
			glass_value = round(float(quantity_value_dict['glass_value']),2)
			polystyrene_value = round(float(quantity_value_dict['polystyrene_value']),2)

			total_house_value = steel_value + copper_value + concrete_value + timber_value + glass_value + polystyrene_value

			

			# building_management_estimation aan de hand van DB query -> is makkelijker

			# Some important calculations
			total_steel_value += steel_value
			total_copper_value += copper_value
			total_timber_value += timber_value
			total_concrete_value += concrete_value
			total_glass_value += glass_value
			total_polystyrene_value += polystyrene_value

			total_steel_quantity += steel_quantity
			total_copper_quantity += copper_quantity
			total_timber_quantity += timber_quantity
			total_concrete_quantity += concrete_quantity
			total_glass_quantity += glass_quantity
			total_polystyrene_quantity += polystyrene_quantity

			total_value += round(float(quantity_value_dict['total_value']),2)

		return render_template("building_management_estimation.html", 
								building_list_db = building_list_db, 
								estimation_list_db = estimation_list_db, 
								total_value = round(float(total_value),2), 
								total_steel_value = round(float(total_steel_value),2),
								total_copper_value = round(float(total_copper_value),2),
								total_timber_value = round(float(total_timber_value),2),
								total_concrete_value = round(float(total_concrete_value),2),
								total_glass_value = round(float(total_glass_value),2),
								total_polystyrene_value = round(float(total_polystyrene_value),2),
								total_steel_quantity = round(float(total_steel_quantity),2),
								total_copper_quantity = round(float(total_copper_quantity),2),
								total_timber_quantity = round(float(total_timber_quantity),2),
								total_concrete_quantity = round(float(total_concrete_quantity),2),
								total_glass_quantity = round(float(total_glass_quantity),2), 
								total_polystyrene_quantity = round(float(total_polystyrene_quantity),2),
								dashboard_used = False
							)





