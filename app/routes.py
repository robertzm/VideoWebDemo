# coding:utf8
from werkzeug.utils import secure_filename

from flask import current_app as app
from flask import make_response, render_template, request, redirect, url_for, flash
import uuid, shortuuid
import sys, os.path
from flask_login import current_user, login_required, login_user, logout_user

from .models import db, MoviePath, MovieInfo, User, SubtitlePath, InvitationCode
from .forms import MoviePathForm, MovieInfoForm, LoginForm, RegistrationForm, SubtitlePathForm, SubtitleInfoForm


# I hate this total mess. Let's get most logic out of here !!!!

@app.route("/", methods=["GET"])
def home():
    return list()


@app.route("/movie/<short>", methods=["GET"])
def index(short):
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))

    existing = MoviePath.query.filter(MoviePath.uuid == short).first()
    info = MovieInfo.query.filter(MovieInfo.uuid == short).first()
    subtitle = SubtitlePath.query.filter(SubtitlePath.uuid == short).first()

    if existing:
        return render_template("home/index.html", file=existing.filepath,
                               movie=info,
                               subtitle=subtitle)
    else:
        return make_response("There's no movie for '{}' existing. ".format(short))


@app.route("/addAll", methods=['GET', 'POST'])
def addAllMovive():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    form = MoviePathForm()
    if form.validate_on_submit():
        if os.path.isdir(os.path.join(sys.path[0], "app", "static", form.path.data)):
            secureAndAddFile(os.path.join(sys.path[0], "app", "static", form.path.data), addMovie)
        else:
            return make_response("Input is not a directory.")
    return render_template("home/addAll.html", form=form)


@app.route("/addSubtitle", methods=['GET', 'POST'])
def addAllSubtitle():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    form = SubtitlePathForm()
    if form.validate_on_submit():
        if os.path.isdir(os.path.join(sys.path[0], "app", "static", form.path.data)):
            secureAndAddFile(os.path.join(sys.path[0], "app", "static", form.path.data), addSubtitle)
        else:
            return make_response("Input is not a directory. ")
    return render_template("home/addAllSubtitle.html", form=form)


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
        return index(uuid)
    return render_template("home/editInfo.html", form=infoForm, uuid=path.uuid, filepath=path.filepath, old=old)


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
    MovieInfo.query.filter(MovieInfo.uuid == uuid).delete()
    db.session.commit()
    return list()


def secureAndAddFile(dir: str, addMethod):
    files = os.listdir(dir)
    for file in files:
        filepath = os.path.join(dir, file)
        if os.path.isdir(filepath):
            secureAndAddFile(filepath, addMethod)
        elif file.startswith('.'):
            pass
        else:
            sf = secure_filename(file)
            newFile = os.path.join(dir, sf)
            if not newFile.__eq__(filepath):
                print("renamed")
                os.rename(filepath, newFile)
            addMethod(newFile)


def addMovie(filepath: str) -> None:
    absPath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = MoviePath.query.filter(MoviePath.filepath == absPath).first()
    if not existing:
        uid = shortuuid.encode(uuid.uuid1())
        record = MoviePath(uuid=uid, filepath=absPath)
        info = MovieInfo(uuid=uid)
        db.session.add(record)
        db.session.add(info)
        db.session.commit()


def addSubtitle(filepath: str) -> None:
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


@app.route('/list', methods=['GET'])
def list():
    if not current_user.is_authenticated:
        return redirect(url_for('loginUser'))
    allMovies = MovieInfo.query.all()
    return render_template("home/list.html", movies=allMovies)


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
