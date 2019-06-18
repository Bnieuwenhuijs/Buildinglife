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

import os, pickle, requests, json, datetime


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

mail = Mail(app)
mail.MAIL_SERVER='smtp.gmail.com'
mail.MAIL_PORT= 465
mail.MAIL_USERNAME= 'buildinglife.no.reply@gmail.com'
mail.MAIL_PASSWORD= 'r2ItgT62'
mail.MAIL_USE_TLS= False
mail.MAIL_USE_SSL= True


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
				flash('User is not confirmed. Please check your email.')
				return redirect(url_for('login'))

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
				#email = form.email.data
				token = s.dumps(form.email.data, salt = 'email-confirm')
				print (token)
				#msg = Message('Confirm Email with BuildingLife', sender = 'hello@buildinglife.nl', recipients = [form.email.data])
				#link = url_for('confirm_email', token = token, _external = True)

				#msg.body = 'Your link is %s' % (link)
				#mail.send(msg)

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
	# WTform for the building characteristics input
	form_building_charachteristics = DashboardInputCharacteristicsForm()

	return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0, name=current_user.username)

@app.route('/dashboard', methods=['GET', 'POST'])
def testing():

	if request.method=='POST':

		# WTform for the building characteristics input
		form_building_charachteristics = DashboardInputCharacteristicsForm()

		building_year = form_building_charachteristics.building_year.data.year
		functionality = form_building_charachteristics.building_functionality.data
		square_meters = form_building_charachteristics.square_meters.data
		nr_floors     = form_building_charachteristics.number_floors.data

		#calculation total square meters
		total_square_meters = nr_floors * square_meters

		#list4 = request.args.get('list2')
		#print(list4)

		if functionality == "Residential":
			funct = 1
		elif functionality == "Office":
			funct = 2
		elif functionality == "Other":
			funct = 3

		# Extract the values of the materials.
		# If not provided, returns null
		Steel       = request.form.get("Steel_input")
		Copper      = request.form.get("Copper_input")
		Concrete    = request.form.get("Concrete_input")
		Timber      = request.form.get("Timber_input")
		Glass       = request.form.get("Glass_input")
		Polystyrene = request.form.get("Polystyrene_input")

		# For later functionality
		#if Steel != None or Steel != "None" or Steel != "":
		#    try:
		#        float(Steel)
		#        float(Copper)
		#        float(Concrete)
		#        float(Timber)
		#        float(Glass)
		#        float(Polystyrene)
		#    except (ValueError, AttributeError, TypeError):
		#        print("ERROR WTF")
		#        flash("Check the flashing mate")
		#        return redirect(url_for('dashboard'))

		# Predictions of material quantity if not provided
		#regression_model_path =  os.path.dirname(os.path.abspath(__file__)) + "\\regression_models"
		regression_model_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "regression_models")

		if Steel == None or Steel == "None" or Steel == "":
			steel_model = pickle.load(open(os.path.join(regression_model_path, "steel_model.sav"), 'rb'))
			Steel = steel_model.predict([[total_square_meters,funct,building_year]])[0]

		if Concrete==None or Concrete == "None" or Concrete == "":
			concrete_model = pickle.load(open(os.path.join(regression_model_path, "concrete_model.sav"), 'rb'))
			Concrete = concrete_model.predict([[total_square_meters,funct,building_year]])[0]

		if Copper==None or Concrete == "None" or Copper == "":
			copper_model = pickle.load(open(os.path.join(regression_model_path, "copper_model.sav") , 'rb'))
			Copper = copper_model.predict([[total_square_meters,funct,building_year]])[0]

		if Glass==None or Glass == "None" or Glass == "":
			glass_model = pickle.load(open(os.path.join(regression_model_path, "glass_model.sav"), 'rb'))
			Glass = glass_model.predict([[total_square_meters,funct,building_year]])[0]

		if Polystyrene==None or Polystyrene == "None" or Polystyrene == "":
			polystyrene_model = pickle.load(open(os.path.join(regression_model_path, "polystyrene_model.sav"), 'rb'))
			Polystyrene = polystyrene_model.predict([[total_square_meters,funct,building_year]])[0]

		if Timber==None or Timber == "None" or Timber == "":
			timber_model = pickle.load(open(os.path.join(regression_model_path, "timber_model.sav"), 'rb'))
			Timber = timber_model.predict([[total_square_meters,funct,building_year]])[0]

		#Value_estimations
		steel_value       = value_calculation(float(Steel), 2, 0.066, 0.1333, 0.86, (datetime.datetime.now().year - building_year ) )
		copper_value      = value_calculation(float(Copper), 5.56, 0.05, 0.1, 1, (datetime.datetime.now().year - building_year ) )
		concrete_value    = value_calculation(float(Concrete), 1.75, 0.02, 0.04, 0.8, (datetime.datetime.now().year - building_year ) )
		timber_value      = value_calculation(float(Timber), 0.9, 0.2, 0.4, 0.66, (datetime.datetime.now().year - building_year ) )
		glass_value       = value_calculation(float(Glass), 1.2, 0.0667, 0.13, 1, (datetime.datetime.now().year - building_year ) )
		polystyrene_value = value_calculation(float(Polystyrene), 1.87, 0.1, 0.2, 0.87, (datetime.datetime.now().year - building_year ) )

		total_list = [steel_value, copper_value, concrete_value, timber_value, glass_value, polystyrene_value]
		total_value = sum(total_list)

		#Put in DB
		building = Building(building_year= building_year, building_functionality= functionality, square_meters= square_meters,
							number_floors= nr_floors,     total_value= round(float(total_value),2),           steel_quantity= round(float(Steel),2),
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

		return render_template('estimation.html',
							   form_build_char=form_building_charachteristics ,
							   numberOfMaterialsDisplayed = 0,
							   total_value = total_value,
							   material_value_dict = material_value_dict,
							   building_year = building_year,
							   functionality = functionality,
							   square_meters = square_meters,
							   number_floors = nr_floors
							   )

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

		return redirect(url_for('purchase'))

	if buy_professional_form.validate_on_submit():
		new_license = License(user_id = current_user.id, 
					  license_type = 'Professional',
					  end_date = datetime.datetime.now() + timedelta(days=365),
					  )

		db.session.add(new_license)
		db.session.commit()

		return redirect(url_for('purchase'))

	if buy_business_form.validate_on_submit():
		new_license = License(user_id = current_user.id, 
					  license_type = 'Business',
					  end_date = datetime.datetime.now() + timedelta(days=365),
					  )

		db.session.add(new_license)
		db.session.commit()

		return redirect(url_for('purchase'))

	return render_template('purchase.html',
		license = license,
		buy_starter_form = buy_starter_form, 
		buy_professional_form = buy_professional_form, 
		buy_business_form = buy_business_form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
	logout_user()
	return redirect(url_for('index'))










