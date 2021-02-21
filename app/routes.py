# coding:utf8
import logging

from flask import current_app as app
from flask import make_response, render_template, request, redirect, url_for, flash
import uuid, shortuuid
import sys, os.path
from flask_login import current_user
from sqlalchemy import asc, desc
import re

from .models import db, MoviePath, SubtitlePath, InvitationCode, MovieInfoV2, MovieInfoV3, Series
from .forms import MoviePathForm, MovieInfoForm, SubtitlePathForm, SubtitleInfoForm, SearchForm, SeriesPathForm

# I hate this total mess. Let's get most logic out of here !!!!
from app.src.util.files import secureAndAddFile, addMovie, addSeries, addSubtitle
from app.src.util.uid import getOrCreateUUID

logger = logging.getLogger('requests')


@app.route("/migrate", methods=['GET', 'POST'])
def migrate():
    allMovies = MovieInfoV2.query.all()
    for movie in allMovies:
        newInfo = MovieInfoV3(uuid=movie.uuid, nameen=movie.nameen,
                              namecn=movie.namecn, year=movie.year,
                              director=movie.director, actor=movie.actor,
                              imdb=movie.imdb, douban=movie.douban,
                              genre=movie.genre, comment=movie.comment)
        db.session.add(newInfo)
        db.session.commit()
    return make_response("migrate done")


@app.route("/", methods=["GET", "POST"])
def home():
    return list()


@app.route("/movie/<short>", methods=["GET"])
def index(short):
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


@app.route("/series/<short>", methods=["GET"])
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


@app.route("/addAll", methods=['GET', 'POST'])
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


@app.route("/addSeries", methods=['GET', 'POST'])
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


@app.route("/addSubtitle", methods=['GET', 'POST'])
def addAllSubtitle():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    form = SubtitlePathForm()
    if form.validate_on_submit():
        if os.path.isdir(os.path.join(sys.path[0], "app", "static", form.path.data)):
            secureAndAddFile(os.path.join(sys.path[0], "app", "static", form.path.data), None, addSubtitle)
        else:
            return make_response("Input is not a directory. ")
    return render_template("home/addAllSubtitle.html", form=form)


@app.route("/movie/edit/<uuid>", methods=['GET', 'POST'])
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
            return watchSeries(uuid)
        else:
            return index(uuid)
    return render_template("home/editInfo.html", form=infoForm, uuid=uuid, filepath=path, old=old)


@app.route("/link/subtitle/<uuid>", methods=['GET', 'POST'])
def editMoviveSubtitle(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    unused = SubtitlePath.query.filter(SubtitlePath.uuid == None)
    form = SubtitleInfoForm()
    form.path.choices = [(subtitle.filepath, subtitle.filepath) for subtitle in unused]
    if form.validate_on_submit():
        old = SubtitlePath.query.filter(SubtitlePath.filepath == form.path.data).first()
        old.uuid = uuid
        old.lang = form.lang.data
        db.session.commit()
        return index(uuid)
    return render_template("home/editSubtitle.html", uuid=uuid, form=form)


@app.route("/subtitle/delete/<uuid>", methods=['GET', 'POST'])
def deleteSubtitle(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    SubtitlePath.query.filter(SubtitlePath.uuid == uuid).delete()
    db.session.commit()
    return index(uuid)


@app.route("/movie/delete/<uuid>", methods=['GET', 'POST'])
def deleteMovie(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    MoviePath.query.filter(MoviePath.uuid == uuid).delete()
    MovieInfoV3.query.filter(MovieInfoV3.uuid == uuid).delete()
    Series.query.filter(Series.uuid == uuid).delete()
    db.session.commit()
    return list()


@app.route('/list', methods=['GET', 'POST'])
def list():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for('list', search=form.search.data))
    searchBy = request.args.get('search')
    if searchBy:
        regexp = r'(.)*(' + re.sub('(,|\.| )+', ')(,|.| )(', searchBy) + ')(.)*'
        allMovies = MovieInfoV3.query.filter(MovieInfoV3.nameen.op('regexp')(regexp) |
                                             MovieInfoV3.namecn.op('regexp')(regexp) |
                                             MovieInfoV3.director.op('regexp')(regexp) |
                                             MovieInfoV3.actor.op('regexp')(regexp)).all()
        return render_template('home/list.html', movies=allMovies, form=form)
    base = MovieInfoV3.query
    sortBy = request.args.get('sortBy')
    order = request.args.get('order')
    if sortBy and sortBy in dir(MovieInfoV3):
        if order == 'asc':
            base = base.order_by(asc(sortBy))
        else:
            base = base.order_by(desc(sortBy))
    directBy = request.args.get('directBy')
    if directBy:
        base = base.filter(MovieInfoV3.director.contains(directBy))
    actBy = request.args.get('actBy')
    if actBy:
        base = base.filter(MovieInfoV3.actor.contains(actBy))
    genre = request.args.get('genre')
    if genre:
        base = base.filter(MovieInfoV3.genre.contains(genre))
    allMovies = base.all()
    return render_template("home/list.html", movies=allMovies, form=form)


@app.route('/generateCode', methods=['GET'])
def generate():
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    uid = shortuuid.encode(uuid.uuid1())
    parent = current_user.username
    invitationCode = InvitationCode(uuid=uid, parent=parent)
    db.session.add(invitationCode)
    db.session.commit()
    flash('Congratulations, you can invite your friend with code: {}'.format(uid))
    return list()
