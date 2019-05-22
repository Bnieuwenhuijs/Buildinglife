from flask import render_template
from flask import request
from app import app
from app import db
from app.models import Building
from app.forms import DashboardInputCharacteristicsForm, DashboardIndividualInputMaterialForm, DashboardInputMaterialsForm
import pickle
from pathlib import Path
import os
import datetime

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

@app.route('/login')
def login():
    return render_template('Login.html')

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

        building_year = form_building_charachteristics.building_year.data.year
        functionality = form_building_charachteristics.building_functionality.data
        square_meters = form_building_charachteristics.square_meters.data
        nr_floors     = form_building_charachteristics.number_floors.data

        #Put in DB
        building = Building(building_year= building_year, building_functionality= functionality, square_meters= square_meters, number_floors= nr_floors)
        db.session.add(building)
        db.session.commit()


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

        # Predictions of material quantity if not provided
        regression_model_path =  os.path.dirname(os.path.abspath(__file__)) + "\\regression_models"
        
        if Steel==None:
            steel_model = pickle.load(open(regression_model_path + "\\steel_model.sav", 'rb'))
            Steel = steel_model.predict([[total_square_meters,funct,building_year]])[0]
        
        if Concrete==None:
            concrete_model = pickle.load(open(regression_model_path + "\\concrete_model.sav", 'rb'))
            Concrete = concrete_model.predict([[total_square_meters,funct,building_year]])[0]

        if Copper==None:
            copper_model = pickle.load(open(regression_model_path + "\\copper_model.sav", 'rb'))
            Copper = copper_model.predict([[total_square_meters,funct,building_year]])[0]

        if Glass==None:
            glass_model = pickle.load(open(regression_model_path + "\\glass_model.sav", 'rb'))
            Glass = glass_model.predict([[total_square_meters,funct,building_year]])[0]

        if Polystyrene==None:
            polystyrene_model = pickle.load(open(regression_model_path + "\\polystyrene_model.sav", 'rb'))
            Polystyrene = polystyrene_model.predict([[total_square_meters,funct,building_year]])[0]

        if Timber==None:
            timber_model = pickle.load(open(regression_model_path + "\\timber_model.sav", 'rb'))
            Timber = timber_model.predict([[total_square_meters,funct,building_year]])[0]


        #Value_estimations
        steel_value       = value_calculation(Steel, 2, 0.066, 0.1333, 0.86, (datetime.datetime.now().year - building_year ) )
        copper_value      = value_calculation(Copper, 5.56, 0.05, 0.1, 1, (datetime.datetime.now().year - building_year ) )
        concrete_value    = value_calculation(Concrete, 1.75, 0.02, 0.04, 0.8, (datetime.datetime.now().year - building_year ) )
        timber_value      = value_calculation(Timber, 0.9, 0.2, 0.4, 0.66, (datetime.datetime.now().year - building_year ) )
        glass_value       = value_calculation(Glass, 1.2, 0.0667, 0.13, 1, (datetime.datetime.now().year - building_year ) )
        polystyrene_value = value_calculation(Polystyrene, 1.87, 0.1, 0.2, 0.87, (datetime.datetime.now().year - building_year ) )

        total_list = [steel_value, copper_value, concrete_value, timber_value, glass_value, polystyrene_value]
        total_value = sum(total_list)
        
        material_value_dict =  [{ "Name" : "Steel", "Quantity" : round(Steel,2),  "Value" : round(steel_value,2)},
                                { "Name" : "Copper", "Quantity" : round(Copper,2), "Value" : copper_value},
                                { "Name" : "Concrete", "Quantity" : Concrete, "Value" : concrete_value},
                                { "Name" : "Timber", "Quantity" : Timber, "Value" : timber_value},
                                { "Name" : "GLass", "Quantity" : Glass, "Value" : glass_value},
                                { "Name" : "Polystyrene", "Quantity" : Polystyrene, "Value" : polystyrene_value}]

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
    