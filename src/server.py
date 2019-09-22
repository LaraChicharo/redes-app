from flask import request
from flask import Flask
from flask import render_template

from database_handler import create_user, check_user_pass


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user_pass(username, password):
            return 'successful login'
        else:
            return 'combination of username/password doesn\'t exists'


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        comp_password = request.form['passwordc']
        if password != comp_password:
            return 'Passwords don\'t match'
        else:
            create_user(username, password)
            return 'user created successfully'
