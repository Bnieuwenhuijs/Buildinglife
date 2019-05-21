from flask import render_template
from flask import request
from app import app
from app.models import User
from app.forms import DashboardInputCharacteristicsForm, DashboardIndividualInputMaterialForm, DashboardInputMaterialsForm
import pickle
from pathlib import Path
import os

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

@app.route('/login')
def login():
    return render_template('Login.html')

LISTK = ["1", "2"]
@app.route('/dashboard')
def dashboard():
    # WTform for the building characteristics input
    form_building_charachteristics = DashboardInputCharacteristicsForm()

    return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0)

@app.route('/dashboard', methods=['GET', 'POST'])
def testing():
   
   if request.method=='POST':
   
        # WTform for the building characteristics input
        form_building_charachteristics = DashboardInputCharacteristicsForm()

        building_year = form_building_charachteristics.building_year.data
        functionality = form_building_charachteristics.building_functionality.data
        square_meters = form_building_charachteristics.square_meters.data
        nr_floors     = form_building_charachteristics.number_floors.data

        total_square_meters = nr_floors * square_meters
        
        #list4 = request.args.get('list2')
        #print(list4)

        if functionality == "Residential":
            funct = 1
        elif functionality == "Office":
            funct = 2
        elif functionality == "Other":
            funct = 3

        Steel       = request.form.get("Steel_input")
        Copper      = request.form.get("Copper_input")
        Concrete    = request.form.get("Concrete_input")
        Timber      = request.form.get("Timber_input")
        Glass       = request.form.get("Glass_input")
        Polystyrene = request.form.get("Polystyrene_input")

        regression_model_path =  os.path.dirname(os.path.abspath(__file__)) + "\\regression_models"
        
        if Steel==None:
            steel_model = pickle.load(open(regression_model_path + "\\steel_model.sav", 'rb'))
            Steel = steel_model.predict([[total_square_meters,funct,building_year.year]])[0]
        
        if Concrete==None:
            concrete_model = pickle.load(open(regression_model_path + "\\concrete_model.sav", 'rb'))
            Concrete = concrete_model.predict([[total_square_meters,funct,building_year.year]])[0]

        if Copper==None:
            copper_model = pickle.load(open(regression_model_path + "\\copper_model.sav", 'rb'))
            Copper = copper_model.predict([[total_square_meters,funct,building_year.year]])[0]

        if Glass==None:
            glass_model = pickle.load(open(regression_model_path + "\\glass_model.sav", 'rb'))
            Glass = glass_model.predict([[total_square_meters,funct,building_year.year]])[0]

        if Polystyrene==None:
            polystyrene_model = pickle.load(open(regression_model_path + "\\polystyrene_model.sav", 'rb'))
            Polystyrene = polystyrene_model.predict([[total_square_meters,funct,building_year.year]])[0]

        if Timber==None:
            timber_model = pickle.load(open(regression_model_path + "\\timber_model.sav", 'rb'))
            Timber = timber_model.predict([[total_square_meters,funct,building_year.year]])[0]

        print(Steel)
        print(Concrete)
        print(Copper)
        print(Glass)
        print(Polystyrene)
        print(Timber)

        return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0)

    