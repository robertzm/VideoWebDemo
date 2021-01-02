#coding:utf8
from werkzeug.utils import secure_filename

from app.home import home
from datetime import datetime as dt

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, FileField
from wtforms.validators import InputRequired

from .models import Movie, db

@app.route("/<short>", methods=["GET"])
def index(short):
    print("I'm here for " + short)
    existing = Movie.query.filter(Movie.short == short).first()

    if existing:
        print("yes")
        return render_template("home/index.html", file=existing.path + '/' + existing.fileName, allMovies=Movie.query.all())

@app.route("/", methods=["GET"])
def addMovie():
    nameEN = request.args.get("nameEN")
    nameCN = request.args.get("nameCN")
    path = request.args.get("path")
    fileName = request.args.get("filename")
    short = request.args.get("short")

    existing = Movie.query.filter(Movie.short == short).first()

    if existing:
        return make_response(f"{short} already exists for movie {nameEN} {nameCN}!")
    else:
        newMovie = Movie(
            nameEN = nameEN,
            nameCN = nameCN,
            path = path,
            fileName = fileName,
            short = short
        )
        db.session.add(newMovie)
        db.session.commit()
        return render_template("home/index.html", file=newMovie.path + '/' + newMovie.fileName, allMovies=Movie.query.all())

class LoginForm(Form):
  nameEN = StringField('name-en', validators=[InputRequired()])
  nameCN = StringField('name-cn')
  path = StringField('path')
  short = StringField('shortname', validators=[InputRequired()])
  file = FileField('file')
  submit = SubmitField('submit')

@app.route("/register", methods=['GET', 'POST'])
def registerMovie():
    form = LoginForm()
    if form.validate_on_submit():
        # TODO: add more validation and default values
        fn = secure_filename(form.file.data)
        newMovie = Movie(
            nameEN = form.nameEN.data,
            nameCN = form.nameCN.data,
            path = form.path.data,
            fileName = fn,
            short = form.short.data
        )
        db.session.add(newMovie)
        db.session.commit()
        return render_template("home/index.html", file=newMovie.path + '/' + newMovie.fileName, allMovies=Movie.query.all())
    return render_template("home/register.html", form=form)
