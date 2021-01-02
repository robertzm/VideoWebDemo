#coding:utf8
from app.home import home
from datetime import datetime as dt

from flask import current_app as app
from flask import make_response, redirect, render_template, request, url_for

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

