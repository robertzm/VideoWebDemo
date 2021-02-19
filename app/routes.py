# coding:utf8
import logging

from werkzeug.utils import secure_filename

from flask import current_app as app
from flask import make_response, render_template, request, redirect, url_for, flash
import uuid, shortuuid
import sys, os.path
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import asc, desc
import re

from .models import db, MoviePath, User, SubtitlePath, InvitationCode, MovieInfoV2, MovieInfoV3, Series
from .forms import MoviePathForm, MovieInfoForm, LoginForm, RegistrationForm, SubtitlePathForm, SubtitleInfoForm, \
    SearchForm, SeriesPathForm

# I hate this total mess. Let's get most logic out of here !!!!
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
        return redirect(url_for('loginUser'))

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
        return redirect(url_for('loginUser'))

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
        return redirect(url_for('loginUser'))
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
        return redirect(url_for('loginUser'))
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


def getOrCreateUUID(dir: str) -> (bool, str):
    files = os.listdir(dir)
    files = [os.path.join(dir, f).split('static')[1].replace('\\', '/')[1:] for f in files]
    allSeries = Series.query.all()
    for episode in allSeries:
        if episode.filepath in files:
            return (True, episode.uuid)
    return (False, shortuuid.encode(uuid.uuid1()))


@app.route("/addSubtitle", methods=['GET', 'POST'])
def addAllSubtitle():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
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
        return redirect(url_for('loginUser'))
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
        return redirect(url_for('loginUser'))
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
        return redirect(url_for('loginUser'))
    SubtitlePath.query.filter(SubtitlePath.uuid == uuid).delete()
    db.session.commit()
    return index(uuid)


@app.route("/movie/delete/<uuid>", methods=['GET', 'POST'])
def deleteMovie(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    MoviePath.query.filter(MoviePath.uuid == uuid).delete()
    MovieInfoV3.query.filter(MovieInfoV3.uuid == uuid).delete()
    Series.query.filter(Series.uuid == uuid).delete()
    db.session.commit()
    return list()


def secureAndAddFile(dir: str, uid: str, addMethod):
    files = os.listdir(dir)
    for file in files:
        filepath = os.path.join(dir, file)
        if os.path.isdir(filepath):
            secureAndAddFile(filepath, uid, addMethod)
        elif file.startswith('.'):
            pass
        else:
            sf = secure_filename(file)
            newFile = os.path.join(dir, sf)
            if not newFile.__eq__(filepath):
                print("renamed")
                os.rename(filepath, newFile)
            addMethod(newFile, uid)


def addMovie(filepath: str, uid: str) -> None:
    absPath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = MoviePath.query.filter(MoviePath.filepath == absPath).first()
    if not existing:
        uid = shortuuid.encode(uuid.uuid1())
        record = MoviePath(uuid=uid, filepath=absPath)
        info = MovieInfoV3(uuid=uid)
        db.session.add(record)
        db.session.add(info)
        db.session.commit()


def addSeries(filepath: str, uid: str) -> None:
    relativePath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = Series.query.filter(Series.filepath == relativePath).first()
    tmp = re.search('\.(S[0-9]*)?E[0-9]*\.', relativePath.upper())
    if tmp:
        episode = tmp[0][1:-1]
    else:
        episode = 'NONE'
    if not existing:
        e = Series(uuid=uid, episode=episode, filepath=relativePath)
        db.session.add(e)
        db.session.commit()


def addSubtitle(filepath: str, uid: str) -> None:
    absPath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = SubtitlePath.query.filter(SubtitlePath.filepath == absPath).first()
    if not existing:
        record = SubtitlePath(filepath=absPath)
        db.session.add(record)
        db.session.commit()


@app.route("/login", methods=['GET', 'POST'])
def loginUser():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('loginUser'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('home/login.html', title='Sign In', form=form)


@app.route('/logout')
def logoutUser():
    logout_user()
    return redirect(url_for('loginUser'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        invitationCode = form.invitationCode.data
        record = InvitationCode.query.filter(InvitationCode.uuid == invitationCode).first()
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        record.used = True
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('loginUser'))
    return render_template('home/register.html', title='Register', form=form)


@app.route('/list', methods=['GET', 'POST'])
def list():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
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
        return redirect(url_for('loginUser'))
    uid = shortuuid.encode(uuid.uuid1())
    parent = current_user.username
    invitationCode = InvitationCode(uuid=uid, parent=parent)
    db.session.add(invitationCode)
    db.session.commit()
    flash('Congratulations, you can invite your friend with code: {}'.format(uid))
    return list()
