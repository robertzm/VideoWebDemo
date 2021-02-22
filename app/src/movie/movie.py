# Blueprint Configuration
import os, sys

from flask import Blueprint, url_for, render_template, make_response
from flask_login import current_user
from sqlalchemy import asc
from werkzeug.utils import redirect

from app import db
from app.src.movie.forms import MoviePathForm, MovieInfoForm
from app.src.movie.models import MoviePath, MovieInfoV3
from app.src.series.models import Series
from app.src.subtitle.models import SubtitlePath
from app.src.util.files import secureAndAddFile, addMovie

movie_bp = Blueprint(
    "movie_bp", __name__, template_folder="templates", static_folder="static"
)

@movie_bp.route("/watch/<short>", methods=["GET"])
def watchMovie(short):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))

    existing = MoviePath.query.filter(MoviePath.uuid == short).first()
    info = MovieInfoV3.query.filter(MovieInfoV3.uuid == short).first()
    subtitle = SubtitlePath.query.filter(SubtitlePath.uuid == short).first()

    if existing:
        return render_template("home/index.html", file=existing.filepath,
                               movie=info,
                               subtitle=subtitle)
    else:
        return make_response("There's no movie for '{}' existing. ".format(short))


@movie_bp.route("/addAll", methods=['GET', 'POST'])
def addAllMovive():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    form = MoviePathForm()
    if form.validate_on_submit():
        if os.path.isdir(os.path.join(sys.path[0], "app", "static", form.path.data)):
            secureAndAddFile(os.path.join(sys.path[0], "app", "static", form.path.data), None, addMovie)
        else:
            return make_response("Input is not a directory.")
    return render_template("home/addAll.html", form=form)


@movie_bp.route("/edit/<uuid>", methods=['GET', 'POST'])
def editMoviveInfo(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    old = MovieInfoV3.query.filter(MovieInfoV3.uuid == uuid).first()
    if not old:
        return make_response("{} doesn't have any old Movie Info".format(uuid))
    if old.isSeries:
        path = Series.query.filter(Series.uuid == uuid).order_by(asc('filepath')).all()
    else:
        path = MoviePath.query.filter(MoviePath.uuid == uuid).all()
    infoForm = MovieInfoForm()
    if infoForm.validate_on_submit():
        old.nameen = infoForm.nameEN.data
        old.namecn = infoForm.nameCN.data
        old.year = infoForm.year.data
        old.director = infoForm.director.data
        old.actor = infoForm.actor.data
        old.genre = infoForm.genre.data
        old.imdb = infoForm.imdb.data
        old.douban = infoForm.douban.data
        db.session.commit()
        if old.isSeries:
            from app.routes import watchSeries
            return watchSeries(uuid)
        else:
            return watchMovie(uuid)
    return render_template("home/editInfo.html", form=infoForm, uuid=uuid, filepath=path, old=old)


@movie_bp.route("/delete/<uuid>", methods=['GET', 'POST'])
def deleteMovie(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    MoviePath.query.filter(MoviePath.uuid == uuid).delete()
    MovieInfoV3.query.filter(MovieInfoV3.uuid == uuid).delete()
    Series.query.filter(Series.uuid == uuid).delete()
    db.session.commit()
    from app.routes import list
    return list()
