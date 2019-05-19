from flask import render_template
from flask import request
from app import app

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
    # Maybe for later
    #login_email    = request.form["inputEmail"]
    #login_password = request.form["inputPassword"]
    return render_template('dashboard.html')

@app.route('/test')
def test():
    print("activated")
    text1 = request.form.get('txtBox_steel')
    print(text1 * 2)
    return render_template('index.html')
    