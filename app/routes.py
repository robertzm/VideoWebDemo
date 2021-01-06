#coding:utf8
from werkzeug.utils import secure_filename

from flask import current_app as app
from flask import make_response, render_template, request, redirect, url_for, flash
import uuid, shortuuid
import sys, os.path
from app import app_url, app_port
from flask_login import current_user, login_required, login_user, logout_user

from .models import db, MoviePath, MovieInfo, User
from .forms import MoviePathForm, MovieInfoForm, LoginForm, RegistrationForm

url = "http://"+app_url+":"+app_port

@app.route("/movie/", methods=["GET"])
def __index():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    allMovies = MovieInfo.query.all()

    if allMovies:
        first = MoviePath.query.filter(MoviePath.uuid == allMovies[0].uuid).first()
        return render_template("home/index.html", file=first.file(), allMovies=allMovies, url=url)
    else:
        return make_response("There's no movie existing at all. ")

@app.route("/movie/<short>", methods=["GET"])
def index(short):
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    existing = MoviePath.query.filter(MoviePath.uuid == short).first()

    if existing:
        return render_template("home/index.html", file=existing.file(), allMovies=MovieInfo.query.all(), url=url)
    else:
        return make_response("There's no movie for '{}' existing. ".format(short))

@app.route("/addAll", methods=['GET', 'POST'])
def addAllMovive():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    form = MoviePathForm()
    if form.validate_on_submit():
        if os.path.isdir(os.path.join(sys.path[0], "app", "static", form.path.data)):
            secureFileName(os.path.join(sys.path[0], "app", "static", form.path.data))
        else:
            return make_response("Input is not a directory." )
    return render_template("home/addAll.html", form=form)

@app.route("/movie/edit/<uuid>", methods=['GET', 'POST'])
def editMoviveInfo(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    path = MoviePath.query.filter(MoviePath.uuid == uuid).first()
    old = MovieInfo.query.filter(MovieInfo.uuid == uuid).first()
    infoForm = MovieInfoForm()
    if infoForm.validate_on_submit():
        old.nameen = infoForm.nameEN.data
        old.namecn = infoForm.nameCN.data
        old.year = infoForm.year.data
        old.director = infoForm.director.data
        db.session.commit()
        return render_template("home/index.html", file=path.file(), allMovies=MovieInfo.query.all(), url=url)
    return render_template("home/editInfo.html", form=infoForm, uuid=path.uuid, filepath=path.filepath)

@app.route("/movie/delete/<uuid>", methods=['GET', 'POST'])
def deleteMovie(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    MoviePath.query.filter(MoviePath.uuid == uuid).delete()
    MovieInfo.query.filter(MovieInfo.uuid == uuid).delete()
    db.session.commit()
    return __index()

def secureFileName(dir):
    files = os.listdir(dir)
    for file in files:
        filepath = os.path.join(dir, file)
        if os.path.isdir(filepath):
            secureFileName(filepath)
        elif file.startswith('.'):
            pass
        else:
            sf = secure_filename(file)
            newFile = os.path.join(dir, sf)
            if not newFile.__eq__(filepath):
                print("renamed")
                os.rename(filepath, newFile)
            existing = MoviePath.query.filter(MoviePath.filepath == newFile).first();
            if not existing:
                uid = shortuuid.encode(uuid.uuid1())
                record = MoviePath(uuid=uid, filepath=newFile)
                info = MovieInfo(uuid=uid)
                db.session.add(record)
                db.session.add(info)
                db.session.commit()


@app.route("/login", methods=['GET', 'POST'])
def loginUser():
    if current_user.is_authenticated:
        return redirect(url_for('__index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('loginUser'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('__index'))
    return render_template('home/login.html', title='Sign In', form=form)

@app.route('/logout')
def logoutUser():
    logout_user()
    return redirect(url_for('loginUser'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('__index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('loginUser'))
    return render_template('home/register.html', title='Register', form=form)


