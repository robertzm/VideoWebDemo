#coding:utf8
from werkzeug.utils import secure_filename

from flask import current_app as app
from flask import make_response, render_template, request
import deprecation
from wtforms import ValidationError

from .models import Movie, db
from .forms import RegisterForm

@app.route("/movie/<short>", methods=["GET"])
def index(short):
    print("I'm here for " + short)
    existing = Movie.query.filter(Movie.short == short).first()

    if existing:
        print("yes")
        return render_template("home/index.html", file=existing.filePath(), allMovies=Movie.query.all())
    else:
        make_response("There's no movie for '{}' existing. ".format(short))

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
        return render_template("home/index.html", file=newMovie.filePath(), allMovies=Movie.query.all())
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
            return render_template("home/index.html", file=newMovie.filePath(), allMovies=Movie.query.all())
        except ValidationError as ve:
            return make_response("Add new Movie failed because: {}".format(ve))
        except Exception as e:
            return make_response("Add new Movie failed and don't know why. Detail: {}".format(e))
    return render_template("home/register.html", form=form)

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

