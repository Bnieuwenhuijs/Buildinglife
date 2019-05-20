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

    return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0)

@app.route('/dashboard', methods=['GET', 'POST'])
def testing():
    # WTform for the building characteristics input
    form_building_charachteristics = DashboardInputCharacteristicsForm()
    
    #list4 = request.args.get('list2')
    #print(list4)

    Steel       = request.form.get("Steel_input")
    Copper      = request.form.get("Copper_input")
    Concrete    = request.form.get("Concrete_input")
    Timber      = request.form.get("Timber_input")
    Glass       = request.form.get("Glass_input")
    Polystyrene = request.form.get("Polystyrene_input")


    print(Steel)
    print(Copper)
    print(Concrete)
    print(Timber)
    print(Glass)
    print(Polystyrene)

    return render_template('dashboard.html', form_build_char=form_building_charachteristics , numberOfMaterialsDisplayed = 0)

    