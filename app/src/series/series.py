# Blueprint Configuration
import os, sys

from flask import Blueprint, url_for, render_template, make_response, request
from flask_login import current_user
from sqlalchemy import asc
from werkzeug.utils import redirect

from app import db
from app.src.movie.models import MovieInfoV3
from app.src.series.forms import SeriesPathForm
from app.src.series.models import Series
from app.src.util.files import secureAndAddFile, addSeries
from app.src.util.uid import getOrCreateUUID

series_bp = Blueprint(
    "series_bp", __name__, template_folder="templates", static_folder="static"
)


@series_bp.route("/watch/<short>", methods=["GET"])
def watchSeries(short):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))

    index = request.args.get('index')
    episode = None
    if index:
        episode = Series.query.filter(Series.uuid == short, Series.episode == index).first()
    if not episode:
        episode = Series.query.filter(Series.uuid == short).order_by(asc('episode')).first()

    info = MovieInfoV3.query.filter(MovieInfoV3.uuid == short).first()
    allSeries = Series.query.filter(Series.uuid == short).order_by(asc('episode')).all()

    if episode:
        return render_template("home/index.html", file=episode.filepath,
                               allSeries=allSeries,
                               movie=info,
                               subtitle=episode.subtitle)
    else:
        return make_response("There's no movie for '{}' existing. ".format(short))


@series_bp.route("/addSeries", methods=['GET', 'POST'])
def allSeries():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    form = SeriesPathForm()
    dir = os.path.join(sys.path[0], "app", "static", form.path.data)
    if form.validate_on_submit():
        if os.path.isdir(dir):
            (exist, uid) = getOrCreateUUID(dir)
            if not exist:
                info = MovieInfoV3(uuid=uid, isSeries=True)
                db.session.add(info)
            secureAndAddFile(dir, uid, addSeries)
        else:
            return make_response("Input is not a directory. ")
    return render_template("home/addSeries.html", form=form)
