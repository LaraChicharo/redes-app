import hashlib
from os import environ

from api import search_movie, search_movie_id
from flask import Flask, render_template, request, session, redirect
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

print('*** ----- ***')
print('*** SECRET KEY SHOULD NOT BE DEFINED HERE IN PRODUCTION ***')
print('*** ----- ***')
app.secret_key = 'blablala'
print('*** SECRET KEY SHOULD NOT BE DEFINED HERE IN PRODUCTION ***')
print('*** ----- ***')

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
        'Movie', secondary=movies, lazy=False,
        backref=db.backref('users', lazy=False)
    )


class Movie(db.Model):
    __tablename__ = 'movie'
    imdbid = db.Column(db.String(64), nullable=False, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    year = db.Column(db.String(64), nullable=True)
    poster = db.Column(db.String(256), nullable=True)


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
        return (True, q.first())
    else:
        return (False, None)


def create_movie(imdbid, title, year, poster):
    new_movie = Movie(imdbid=imdbid, title=title, year=year, poster=poster)
    db.session.add(new_movie)
    db.session.commit()
    return new_movie


def add_wishlist(userid, movie):
    user = User.query.filter(User.id == userid).first()
    user.movies.append(movie)
    db.session.add(user)
    db.session.commit()


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
        exists, user = check_user_pass(username, password)
        if exists:
            session['username'] = user.username
            session['userid'] = user.id
            return render_template('index.html')
        else:
            return 'combination of username/password doesn\'t exists'


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    session.pop('userid', None)
    return render_template('index.html')


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
    if success :
        userid = session.get('userid')
        return render_template(
            'results.html', results=res['Search'], query=mquery, userid=userid
        )
    else:
        return (res, status_code)


@app.route('/add-wishlist', methods=['POST'])
def add_wishlist_route():
    if request.method == 'POST':
        userid = request.form['userid']
        movie_imdbid = request.form['movieid']
        movietitle = request.form['movietitle']
        movieyear = request.form['movieyear']
        movieposter = request.form['movieposter']

        movie = Movie.query.filter(Movie.imdbid == movie_imdbid).first()
        if not movie:
            movie = create_movie(
                movie_imdbid, movietitle, movieyear, movieposter
            )
        add_wishlist(userid, movie)
        return redirect('/wish')


@app.route('/wish')
def wish_list():
    if session.get('username'):
        user = User.query.filter(User.id == session['userid']).first()
        return render_template(
            'wish_list.html', movies=user.movies, nmovies=len(user.movies)
        )
    else:
        return redirect('/login')


@app.route('/movie/<imdbid>')
def movie_detail(imdbid):
    status_code, success, res = search_movie_id(imdbid)
    if success:
        return render_template('movie_detail.html', movie=res, status_code=200)
    else:
        return (res, status_code)

 
if __name__ == '__main__':
    app.run(debug=True)
