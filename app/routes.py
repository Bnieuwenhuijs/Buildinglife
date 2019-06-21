#!flask/bin/python

from flask import render_template
from flask import request, flash, redirect, url_for

from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

from app import app
from app import db
from app.models import Building, User, License
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
				flash('Your login/password does not match or exists')
			elif not user.isConfirmed:
				flash('Your account is not confirmed yet. Check your email')

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
					flash('Please use a valid email', 'error')
					return render_template('signup.html', form = form)
				'''

				server.sendmail(MAIL_USERNAME, form.email.data, email)
				server.quit() 

				db.session.add(new_user)
				db.session.commit()
				flash('You successfully created your account. Check your email to confirm it.')
			else:
				flash('There is already an account with that email')
		else:
			flash('There is already an account with that username')
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
	return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0, name=current_user.username)

windowchecked = False
buildingManagementUsed = False
building_properties_list = []
@app.route('/dashboard', methods=['GET', 'POST'])
def testing():

	if request.method=='POST':

		# WTform for the building characteristics input
		form_building_charachteristics = DashboardInputCharacteristicsForm()

		# Get the location information
		postalcode = form_building_charachteristics.postalcode.data
		city = form_building_charachteristics.city.data
		housenumber = form_building_charachteristics.housenumber.data
		streetname = form_building_charachteristics.streetname.data

		global windowchecked
		print("IK BEN HIER 1")
		windowchecked = request.form.get("windowcount") != None
		print(windowchecked)
		print("IK BEN HIER 2")

		global buildingManagementUsed
		buildingManagementUsed = False

		# Get the cordinates
		gebruiksdoel_Oppervlakte_data = requests.get('http://geodata.nationaalgeoregister.nl/locatieserver/free?rows=1&&fq=postcode:' + postalcode + '&&fq=huisnummer:' + housenumber + '&&fq=type:adres'
		).json()

		if list(gebruiksdoel_Oppervlakte_data)[0] == 'error':
			# Flask message here.
			return ('', 204)

		response = gebruiksdoel_Oppervlakte_data["response"]

		# Check if a valid building has been provided
		if (response["numFound"] == 0):
			return ('', 204)
		
		# Get the cordinates in the format (Point(Y-cordinate, X-cordinate))
		cordinates = response['docs'][0]['centroide_ll']

		x_cordinate = cordinates[int(cordinates.index(' ')) + 1 : int(cordinates.index(')'))]
		y_cordinate = cordinates[int(cordinates.index('(')) + 1 : int(cordinates.index(' '))]
		cordinates = x_cordinate + "," + y_cordinate

		# Create the list with building location information
		buildingList = [[cordinates, streetname, postalcode, housenumber, city]]
		

		# Create the list with characteristics
		global building_properties_list
		building_properties_list = []
		building_properties_list.append(get_building_properties(postalcode, 
										housenumber, 
										windowchecked))	

		# Extract the values of the materials.
		# If not provided, returns null
		global Steel
		global Copper
		global Concrete
		global Timber
		global Glass
		global Polystyrene
		Steel       = request.form.get("Steel_input")
		Copper      = request.form.get("Copper_input")
		Concrete    = request.form.get("Concrete_input")
		Timber      = request.form.get("Timber_input")
		Glass       = request.form.get("Glass_input")
		Polystyrene = request.form.get("Polystyrene_input")

		return render_template("parameters.html", buildingList = buildingList, building_properties_list = building_properties_list)

@app.route('/history')
def history():
	buildings = Building.query.order_by(Building.id.desc())

	return render_template('history.html', buildings=buildings)

@app.route('/BuildingManagement')
def BuildingManagement():

	BMform = BuildingManagementForm()

	headers = {'Content-Type': 'application/json'}
	response = requests.get('http://geodata.nationaalgeoregister.nl/locatieserver/free?fq=postcode:3452AM', headers=headers)

	if response.status_code == 200:
		print (json.loads(response.content.decode('utf-8')) )
	else:
		print("Got an error")

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
	
buildingList = []
@app.route('/postlocationdata', methods = ['POST'])
def get_post_location_data():

	global buildingManagementUsed 
	buildingManagementUsed = True

	jsdata = request.form['javascript_data']
	global windowchecked
	windowchecked = request.form['window_checked_data'][0] == "t"

	global buildingList
	# BuildingList is a list which consists of lists of (cordinates, street, postalcode, streetnumber, city)
	# As example: [['POINT(4.93932396 51.54225764)', 'Oranjestraat', '5126bl', '5', 'Gilze']]
	buildingList = json.loads(jsdata)

	return "/parameters"

building_properties_list = []
@app.route('/parameters')
def parameters():

	global building_properties_list

	building_properties_list = []
	buildings = len(buildingList)

	for building in range(buildings):
		building_properties_list.append(get_building_properties(str(buildingList[building][2]), 
										str(buildingList[building][3]), 
										window_count = windowchecked)
										)
	#building_properties_list is a list with dictionaries. example: 
	# [{'square_meters': 143, 'building_functionality': 'woonfunctie',
	#  'Place_name': 'Vleuten', 'Building_year': 2005, 'ground-0.50': 0.26, 
	# 'roof-0.25': 6.45, 'rmse-0.25': 1.26, 
	# 'roof-0.75': 9.15, 'rmse-0.75': 1.22, 'roof-0.95': 10.24,
	# 'rmse-0.95': 1.22, 'roof_flat': False}]

	return render_template("parameters.html", buildingList = buildingList, building_properties_list = building_properties_list)

@app.route('/building_management_estimation')
def building_management_estimation():

	regression_model_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "regression_models")

	# Create list to store values in
	material_value_dict = []

	# Models when window is available
	steel_window_model = pickle.load(open(os.path.join(regression_model_path, "steel_window_model.sav"), 'rb'))
	copper_window_model = pickle.load(open(os.path.join(regression_model_path, "copper_window_model.sav"), 'rb'))
	timber_window_model = pickle.load(open(os.path.join(regression_model_path, "timber_window_model.sav"), 'rb'))
	concrete_window_model = pickle.load(open(os.path.join(regression_model_path, "concrete_window_model.sav"), 'rb'))
	glass_window_model = pickle.load(open(os.path.join(regression_model_path, "glass_window_model.sav"), 'rb'))
	concrete_window_model = pickle.load(open(os.path.join(regression_model_path, "copper_window_model.sav"), 'rb'))
	polystyrene_window_model = pickle.load(open(os.path.join(regression_model_path, "polystyrene_window_model.sav"), 'rb'))

	# Models when window is not available
	steel_model = pickle.load(open(os.path.join(regression_model_path, "steel_model.sav"), 'rb'))
	copper_model = pickle.load(open(os.path.join(regression_model_path, "copper_model.sav"), 'rb'))
	timber_model = pickle.load(open(os.path.join(regression_model_path, "timber_model.sav"), 'rb'))
	concrete_model = pickle.load(open(os.path.join(regression_model_path, "concrete_model.sav"), 'rb'))
	glass_model = pickle.load(open(os.path.join(regression_model_path, "glass_model.sav"), 'rb'))
	polystyrene_model = pickle.load(open(os.path.join(regression_model_path, "polystyrene_model.sav"), 'rb'))

	# Loop over all the building characteristics of each building that is taken into consideration
	global building_properties_list

	total_value = 0
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

	global buildingManagementUsed 

	if buildingManagementUsed == False:
		# Declare building characteristic variables
		square_meters = building_properties_list[0]['square_meters']
		city = building_properties_list[0]['Place_name']
		building_year = building_properties_list[0]['Building_year']
		ground_050 = building_properties_list[0]['ground_0_50']
		roof_025 = building_properties_list[0]['roof_0_25']
		roof_075 = building_properties_list[0]['roof_0_75']
		roof_095 = building_properties_list[0]['roof_0_95']
		functionality = building_properties_list[0]['building_functionality'].lower()

		if building_properties_list[0]['roof_flat'] == False :
			roof_flat = 0
		else:
			roof_flat = 1

		if functionality == "woonfunctie":
			building_func = 1
		elif functionality == "winkelfunctie":
			building_func = 2
		elif functionality == "industriefunctie":
			building_func = 3
		else:
			building_func = 4

		# Get the global variables
		global Steel
		global Copper
		global Concrete
		global Timber
		global Glass
		global Polystyrene

		# Get the global windowchecked variable
		global windowchecked

		if windowchecked == True and building_properties_list[0]['windows'] > 0:
				windows = building_properties_list[0]['windows']

				print("Windows are taken into account")

				if Steel == None or Steel == "None" or Steel == "":
					Steel = abs(steel_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				if Concrete==None or Concrete == "None" or Concrete == "":
					Concrete = abs(concrete_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				if Copper==None or Copper == "None" or Copper == "":
					Copper = abs(copper_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				if Glass==None or Glass == "None" or Glass == "":
					Glass = abs(glass_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				if Polystyrene==None or Polystyrene == "None" or Polystyrene == "":
					Polystyrene = abs(polystyrene_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				if Timber==None or Timber == "None" or Timber == "":
				 	Timber = abs(timber_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])			

		elif windowchecked == False:
				if Steel == None or Steel == "None" or Steel == "":
					Steel = abs(steel_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				if Concrete==None or Concrete == "None" or Concrete == "":
					Concrete = abs(concrete_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				if Copper==None or Copper == "None" or Copper == "":
					Copper = abs(copper_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				if Glass==None or Glass == "None" or Glass == "":
					Glass = abs(glass_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				if Polystyrene==None or Polystyrene == "None" or Polystyrene == "":
					Polystyrene = abs(polystyrene_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				if Timber==None or Timber == "None" or Timber == "":
				 	Timber = abs(timber_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])			

		# Convert materials per squared meters to total.
		Steel *= square_meters
		Copper *= square_meters
		Concrete *= square_meters
		Timber *= square_meters
		Glass *= square_meters
		Polystyrene *= square_meters


		#Value_estimations
		steel_value       = value_calculation(float(Steel), 2, 0.066, 0.1333, 0.86, (datetime.datetime.now().year - building_year ) )
		copper_value      = value_calculation(float(Copper), 5.56, 0.05, 0.1, 1, (datetime.datetime.now().year - building_year ) )
		concrete_value    = value_calculation(float(Concrete), 1.75, 0.02, 0.04, 0.8, (datetime.datetime.now().year - building_year ) )
		timber_value      = value_calculation(float(Timber), 0.9, 0.2, 0.4, 0.66, (datetime.datetime.now().year - building_year ) )
		glass_value       = value_calculation(float(Glass), 1.2, 0.0667, 0.13, 1, (datetime.datetime.now().year - building_year ) )
		polystyrene_value = value_calculation(float(Polystyrene), 1.87, 0.1, 0.2, 0.87, (datetime.datetime.now().year - building_year ) )
		
		total_list = [steel_value, copper_value, concrete_value, timber_value, glass_value, polystyrene_value]
		total_value = sum(total_list)

		nr_floor = round((roof_095 - ground_050) / 3)

		#Put in DB
		building = Building(building_year= building_year, building_functionality= building_func, square_meters= square_meters,
                           	 number_floors= nr_floor,     total_value= round(float(total_value),2),           steel_quantity= round(float(Steel),2),
                         	 steel_Value=          round(float(steel_value),2),    copper_quantity=      round(float(Copper),2),
                             copper_Value=         round(float(copper_value),2),   concrete_quantity=    round(float(Concrete),2),
                             concrete_Value=       round(float(concrete_value),2), timber_quantity=      round(float(Timber),2),
                             timber_Value=         round(float(timber_value),2),   glass_quantity=       round(float(Glass),2),
                             glass_Value=          round(float(glass_value),2),    polystyrene_quantity= round(float(Polystyrene),2),
                             polystyrene_Value=    round(float(polystyrene_value),2))
							
		db.session.add(building)
		db.session.commit()

		material_value_dict =  [{ "Name" : "Steel", "Quantity" : round(float(Steel),2),  "Value" : round(float(steel_value),2)},
                                { "Name" : "Copper", "Quantity" : round(float(Copper),2), "Value" : round(float(copper_value),2)},
                                { "Name" : "Concrete", "Quantity" : round(float(Concrete),2), "Value" : round(float(concrete_value),2)},
                                { "Name" : "Timber", "Quantity" : round(float(Timber),2), "Value" : round(float(timber_value),2)},
                                { "Name" : "GLass", "Quantity" : round(float(Glass),2), "Value" : round(float(glass_value),2)},
                                { "Name" : "Polystyrene", "Quantity" : round(float(Polystyrene),2), "Value" : round(float(polystyrene_value),2)}]

		nr_floor = round((roof_095 - ground_050) / 3)

		return render_template('estimation.html',
                               total_value = total_value,
                               material_value_dict = material_value_dict,
                               building_year = building_year,
                               functionality = building_func,
                               square_meters = square_meters,
                               number_floors = nr_floor
                               )


		

	elif buildingManagementUsed  == True:
		for building in building_properties_list:

			square_meters = building['square_meters']
			city = building['Place_name']
			building_year = building['Building_year']
			ground_050 = building['ground_0_50']
			roof_025 = building['roof_0_25']
			roof_075 = building['roof_0_75']
			roof_095 = building['roof_0_95']
			functionality = building['building_functionality'].lower()

		

			if building['roof_flat'] == False :
				roof_flat = 0
			else:
				roof_flat = 1

			if functionality == "woonfunctie":
				building_func = 1
			elif functionality == "winkelfunctie":
				building_func = 2
			elif functionality == "industriefunctie":
				building_func = 3
			else:
				building_func = 4


			if windowchecked == True and building['windows'] > 0:
				windows = building['windows']

				Steel = abs(steel_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				Copper = abs(copper_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				Concrete = abs(concrete_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				Timber = abs(timber_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				Glass = abs(glass_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				Polystyrene = abs(polystyrene_window_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters, windows]])[0])
				
			elif windowchecked == False:
				Steel = abs(steel_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat, square_meters]])[0])
				Copper = abs(copper_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				Concrete = abs(concrete_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				Timber = abs(timber_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				Glass = abs(glass_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])
				Polystyrene = abs(polystyrene_model.predict([[building_year,building_func,ground_050,roof_025,roof_075,roof_095,roof_flat,square_meters]])[0])			

			# Convert materials per squared meters to total.
			Steel *= square_meters
			Copper *= square_meters
			Concrete *= square_meters
			Timber *= square_meters
			Glass *= square_meters
			Polystyrene *= square_meters

			## Calculate the values of the materials
			# Calculate the amount of years that have passed between the building year and current year
			time_passed = datetime.datetime.now().year - building_year

			steel_value       = value_calculation(float(Steel), 2, 0.066, 0.1333, 0.86, time_passed)
			copper_value      = value_calculation(float(Copper), 5.56, 0.05, 0.1, 1, time_passed )
			concrete_value    = value_calculation(float(Concrete), 1.75, 0.02, 0.04, 0.8, time_passed )
			timber_value      = value_calculation(float(Timber), 0.9, 0.2, 0.4, 0.66, time_passed )
			glass_value       = value_calculation(float(Glass), 1.2, 0.0667, 0.13, 1, time_passed )
			polystyrene_value = value_calculation(float(Polystyrene), 1.87, 0.1, 0.2, 0.87, time_passed )
		
			material_value_dict.append([{ "Name" : "Steel", "Quantity" : round(float(Steel),2),  "Value" : round(float(steel_value),2)},
                                		{ "Name" : "Copper", "Quantity" : round(float(Copper),2), "Value" : round(float(copper_value),2)},
                                		{ "Name" : "Concrete", "Quantity" : round(float(Concrete),2), "Value" : round(float(concrete_value),2)},
                                		{ "Name" : "Timber", "Quantity" : round(float(Timber),2), "Value" : round(float(timber_value),2)},
                                		{ "Name" : "GLass", "Quantity" : round(float(Glass),2), "Value" : round(float(glass_value),2)},
                                		{ "Name" : "Polystyrene", "Quantity" : round(float(Polystyrene),2), "Value" : round(float(polystyrene_value),2)}]
										)

			total_house_value = steel_value + copper_value + concrete_value + timber_value + glass_value + polystyrene_value

			nr_floor = round((roof_095 - ground_050) / 3)

			#Put in DB
			building = Building(building_year= building_year, building_functionality= building_func, square_meters= square_meters,
                           	 number_floors= nr_floor,     total_value= round(float(total_value),2),           steel_quantity= round(float(Steel),2),
                         	 steel_Value=          round(float(steel_value),2),    copper_quantity=      round(float(Copper),2),
                             copper_Value=         round(float(copper_value),2),   concrete_quantity=    round(float(Concrete),2),
                             concrete_Value=       round(float(concrete_value),2), timber_quantity=      round(float(Timber),2),
                             timber_Value=         round(float(timber_value),2),   glass_quantity=       round(float(Glass),2),
                             glass_Value=          round(float(glass_value),2),    polystyrene_quantity= round(float(Polystyrene),2),
                             polystyrene_Value=    round(float(polystyrene_value),2))
							
			db.session.add(building)
			db.session.commit()


			# Some important calculations
			total_steel_value += steel_value
			total_copper_value += copper_value
			total_timber_value += timber_value
			total_concrete_value += concrete_value
			total_glass_value += glass_value
			total_polystyrene_value += polystyrene_value

			total_steel_quantity += Steel
			total_copper_quantity += Copper
			total_timber_quantity += Timber
			total_concrete_quantity += Concrete
			total_glass_quantity += Glass
			total_polystyrene_quantity += Polystyrene

			total_value += (steel_value + copper_value + concrete_value + timber_value + glass_value + polystyrene_value)

		global buildingList
		return render_template("building_management_estimation.html", 
								buildingList = buildingList, 
								material_value_dict = material_value_dict, 
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
								total_polystyrene_quantity = round(float(total_polystyrene_quantity),2)
							)





