#coding:utf8
from werkzeug.utils import secure_filename

from flask import current_app as app
from flask import make_response, render_template, request
import deprecation
from wtforms import ValidationError
import uuid, shortuuid
import sys, os.path
from app import app_url, app_port

from .models import Movie, db, MoviePath, MovieInfo
from .forms import RegisterForm, MoviePathForm, MovieInfoForm

url = "http://"+app_url+":"+app_port

@app.route("/movie/", methods=["GET"])
def __index():
    allMovies = MovieInfo.query.all()

    if allMovies:
        first = MoviePath.query.filter(MoviePath.uuid == allMovies[0].uuid).first()
        return render_template("home/index.html", file=first.file(), allMovies=allMovies, url=url)
    else:
        return make_response("There's no movie existing at all. ")

@app.route("/movie/<short>", methods=["GET"])
def index(short):
    existing = MoviePath.query.filter(MoviePath.uuid == short).first()

    if existing:
        return render_template("home/index.html", file=existing.file(), allMovies=MovieInfo.query.all(), url=url)
    else:
        return make_response("There's no movie for '{}' existing. ".format(short))

@app.route("/", methods=["GET"])
@deprecation.deprecated(deprecated_in="1.x", removed_in="2.0",
                        current_version="1.0",
                        details="Use 'RegisterMovie()' instead.")
def addMovie():
    nameEN = request.args.get("nameEN")
    nameCN = request.args.get("nameCN")
    path = request.args.get("path")
    fileName = request.args.get("filename")
    short = request.args.get("short")

    try:
        newMovie = validateAndAddMovie(nameEN, nameCN, path, fileName, short)
        return render_template("home/index.html", file=newMovie.filePath(), allMovies=Movie.query.all(), url=url)
    except ValidationError as ve:
        return make_response("Add new Movie failed because: {}".format(ve))
    except Exception as e:
        return make_response("Add new Movie failed and don't know why. Detail: {}".format(e))

@app.route("/register", methods=['GET', 'POST'])
def registerMovie():
    form = RegisterForm()
    if form.validate_on_submit():
        fn = secure_filename(form.file.data)
        try:
            newMovie = validateAndAddMovie(form.nameEN.data, form.nameCN.data, form.path.data, fn, form.short.data)
            return render_template("home/index.html", file=newMovie.filePath(), allMovies=Movie.query.all(), url=url)
        except ValidationError as ve:
            return make_response("Add new Movie failed because: {}".format(ve))
        except Exception as e:
            return make_response("Add new Movie failed and don't know why. Detail: {}".format(e))
    return render_template("home/register.html", form=form)

@app.route("/addAll", methods=['GET', 'POST'])
def addAllMovive():
    form = MoviePathForm()
    if form.validate_on_submit():
        if os.path.isdir(os.path.join(sys.path[0], "app", "static", form.path.data)):
            secureFileName(os.path.join(sys.path[0], "app", "static", form.path.data))
        else:
            return make_response("Input is not a directory." )
    return render_template("home/addAll.html", form=form)

@app.route("/movie/edit/<uuid>", methods=['GET', 'POST'])
def editMoviveInfo(uuid):
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

def validateAndAddMovie(nameEN: str, nameCN: str, path: str, filename: str, short: str):
    if nameEN is None:
        raise ValidationError("Name in EN must not be null. ")
    if short is None:
        raise ValidationError("Short Name must not be null. ")

    existName = Movie.query.filter(Movie.nameEN == nameEN).first()
    existShort = Movie.query.filter(Movie.short == short).first()

    if existName:
        raise ValidationError("File: {} already exists, adding movie failed. ".format(nameEN))
    if existShort:
        raise ValidationError("ShortName: {} already exists. Can not use it to add new movie. ".format(short))

    newMovie = Movie(nameEN=nameEN, nameCN=nameCN, path=path, fileName=filename, short=short)
    db.session.add(newMovie)
    db.session.commit()
    return newMovie

