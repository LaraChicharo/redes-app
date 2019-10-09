import hashlib
from os import environ

from api import search_movie, search_movie_id
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


POSTGRES_USER = environ['POSTGRES_USER']
POSTGRES_PW = environ['POSTGRES_PW']
POSTGRES_URL = environ['POSTGRES_URL']
POSTGRES_DB = environ['POSTGRES_DB']

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(
    user=POSTGRES_USER,
    pw=POSTGRES_PW,
    url=POSTGRES_URL,
    db=POSTGRES_DB
)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


movies = db.Table(
    'movies',
    db.Column(
        'userid', db.Integer, db.ForeignKey('user.id'), primary_key=True
    ),
    db.Column(
        'imdbid',
        db.String(64), db.ForeignKey('movie.imdbid'), primary_key=True
    )
)


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=False, nullable=False)
    password = db.Column(db.String(256), index=False, nullable=False)
    movies = db.relationship(
        'Movie', secondary=movies, lazy='subquery',
        backref=db.backref('users', lazy=True)
    )


class Movie(db.Model):
    __tablename__ = 'movie'
    imdbid = db.Column(db.String(64), nullable=False, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    year = db.Column(db.Integer, nullable=True)


db.create_all()


def create_user(username, password):
    password = hashlib.sha256(password.encode()).hexdigest()
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()


def check_user_pass(username, password):
    password = hashlib.sha256(password.encode()).hexdigest()
    q = User.query.filter(
        User.username == username and User.password == password
    )
    if q.first():
       return True
    else:
        return False


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


@app.route('/search')
def search():
    mquery = request.args['mquery']
    if len(mquery) < 3:
        return ('Query too short', 400)
    
    status_code, success, res = search_movie(mquery)
    if success:
        return render_template(
            'results.html', results=res['Search'], query=mquery
        )
    else:
        return (res, status_code)


@app.route('/wish')
def wish_list():
    return render_template('wish_list.html')
    # return render_template('wish_list.html', user=user, movies=movies)


@app.route('/movie/<imdbid>')
def movie_detail(imdbid):
    status_code, success, res = search_movie_id(imdbid)
    if success:
        return render_template('movie_detail.html', movie=res, status_code=200)
    else:
        return (res, status_code)

 
if __name__ == '__main__':
    app.run(debug=True)
