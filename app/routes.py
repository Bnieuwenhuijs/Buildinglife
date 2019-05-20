from flask import render_template
from flask import request
from app import app
from app.forms import DashboardInputCharacteristicsForm, DashboardIndividualInputMaterialForm, DashboardInputMaterialsForm

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

    # Create a list for all the materials for the FieldList
    building_materials = [{"material": "Steel"},
                          {"material": "Copper"},
                          {"material": "Concrete"},
                          {"material": "Timber"},
                          {"material": "Aluminium"},
                          {"material": "Plastic"},
                          {"material": "Clay"},
                          {"material": "Glass"},
                          {"material": "Polystyrene"},
                          {"material": "Drywall"},
                          {"material": "Rubber"},
                          {"material": "Lead"},
                          {"material": "Nickel"},
                          {"material": "Titanium"},
                          {"material": "Brass"},
                          {"material": "Iron"}
                         ]

    print("we zitten in de oorspronkelijke")

    form_building_materials = DashboardInputMaterialsForm(building_materials=building_materials)
    return render_template('dashboard.html', form_build_char=form_building_charachteristics , form_build_mat=form_building_materials, testNR = 0)

@app.route('/dashboard', methods=['GET', 'POST'])
def testing():
    # WTform for the building characteristics input
    form_building_charachteristics = DashboardInputCharacteristicsForm()

    form_building_materials = DashboardInputMaterialsForm()
    
    #list4 = request.args.get('list2')
    #print(list4)

    Steel = request.form.get("Steel_input")
    print(Steel)

    return render_template('dashboard.html', form_build_char=form_building_charachteristics , form_build_mat=form_building_materials, testNR = 0)

    