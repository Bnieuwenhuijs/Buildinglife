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

from datetime import timedelta
import os, pickle, requests, json, datetime, smtplib, ssl


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT= 465
MAIL_USERNAME= 'buildinglife.no.reply@gmail.com'
MAIL_PASSWORD= 'r2ItgT62'
MAIL_USE_TLS= False
MAIL_USE_SSL= True


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

def create_user_welcome_email(name, surname, to, link):
	gmail_password = MAIL_PASSWORD

	user_full_name = name + " " + surname

	email_body = "\r\nCongratulations " + user_full_name + "!\n" +\
				"We've successfully created your account!\n" +\
				"Click this link: " + link + "\nto confirm your email with BuildingLife.\n\n"""+\
				"Thanks,\nBuildingLife Team."

	composed = 	'From: ' + MAIL_USERNAME + '\n' + \
				'To: '+ to +'\n' +\
				'Subject: Welcome to BuildingLife' +\
				email_body + '\n'

	return composed


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

				email = create_user_welcome_email(form.name.data, form.surname.data, form.email.data, link)

				if not validate_email(form.email.data, verify = True):
					flash('Please use a valid email', 'error')
					return render_template('signup.html', form = form)

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

@app.route('/confirm_email/<token>')
def confirm_email(token):
	try:
		# 60*15, the link is active for 15 minutes
		email = s.loads(token, salt = 'email-confirm', max_age=900)
		user = User.query.filter_by(email=email).first()
		user.isConfirmed = True
		db.session.add(user)
		db.session.commit()
		return '<h1>User %s is now confirmed!</h1>' % (user.username)
	except SignatureExpired:
		return '<h1>Token expired </h1>'
	except BadTimeSignature:
		return '<h1>Such token doesn\' exist! </h1>'

@app.route('/dashboard')
def dashboard():
	form_building_charachteristics = DashboardInputCharacteristicsForm()
	return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0, name=current_user.username)

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
		windowchecked = request.form.get("windowcount") != None

		# Get the cordinates
		gebruiksdoel_Oppervlakte_data = requests.get('http://geodata.nationaalgeoregister.nl/locatieserver/free?rows=1&&fq=postcode:' + postalcode + '&&fq=huisnummer:' + housenumber + '&&fq=type:adres'
		).json()

		# get a response
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
		building_properties_list = []
		building_properties_list.append(get_building_properties(postalcode, 
										housenumber, 
										window_count = windowchecked))

		# {'square_meters': 143, 
		# 'building_functionality': 'woonfunctie', 
		# 'Place_name': 'Gilze', 
		# 'Building_year': 1920, 
		# 'ground_0_50': 16.63, 
		# 'roof_0_25': 20.71, 
		# 'rmse_0_25': 1.09, 
		# 'roof_0_75': 22.65, 
		# 'rmse_0_75': 1, 
		# 'roof_0_95': 23.7, 
		# 'rmse_0_95': 0.98, 
		# 'roof_flat': False}

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

		print(buildingList)
		print(building_properties_list)
		return render_template("parameters.html", buildingList = buildingList, building_properties_list = building_properties_list)

@app.route('/history')
def history():
	buildings = Building.query.order_by(Building.id.desc())
	print(buildings)
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
windowchecked = False
@app.route('/postlocationdata', methods = ['POST'])
def get_post_location_data():

	jsdata = request.form['javascript_data']
	global windowchecked
	windowchecked = request.form['window_checked_data'][0] == "t"

	global buildingList
	# BuildingList is a list which consists of lists of (cordinates, street, postalcode, streetnumber, city)
	# As example: [['POINT(4.93932396 51.54225764)', 'Oranjestraat', '5126bl', '5', 'Gilze']]
	buildingList = json.loads(jsdata)

	return "/parameters"


@app.route('/parameters')
def parameters():

	print(windowchecked)
	building_properties_list = []
	buildings = len(buildings)
	print(windowchecked)
	for building in range(buildings):
		building_properties_list.append(get_building_properties(str(buildingList[building][2]), 
										str(buildingList[building][3]), 
										window_count = windowchecked)
										)
	print(building_properties_list)
	#building_properties_list is a list with dictionaries. example: 
	# [{'square_meters': 143, 'building_functionality': 'woonfunctie',
	#  'Place_name': 'Vleuten', 'Building_year': 2005, 'ground-0.50': 0.26, 
	# 'roof-0.25': 6.45, 'rmse-0.25': 1.26, 
	# 'roof-0.75': 9.15, 'rmse-0.75': 1.22, 'roof-0.95': 10.24,
	# 'rmse-0.95': 1.22, 'roof_flat': False}]

	return render_template("parameters.html", buildingList = buildingList, building_properties_list = building_properties_list)

@app.route('/building_management_estimation')
def building_management_estimation():
	return render_template("building_management_estimation.html")





