# coding:utf8
import logging

from flask import current_app as app
from flask import make_response, render_template, request, redirect, url_for
from flask_login import current_user
from sqlalchemy import asc, desc
import sys, os.path
import re

from .models import db, SubtitlePath
from .forms import SubtitlePathForm, SubtitleInfoForm, SearchForm

# I hate this total mess. Let's get most logic out of here !!!!
from app.src.util.files import secureAndAddFile, addSeries, addSubtitle
from .src.movie.models import MovieInfoV3
from .src.movie.movie import watchMovie

logger = logging.getLogger('requests')


@app.route("/", methods=["GET", "POST"])
def home():
    return list()



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
        return watchMovie(uuid)
    return render_template("home/editSubtitle.html", uuid=uuid, form=form)


@app.route("/subtitle/delete/<uuid>", methods=['GET', 'POST'])
def deleteSubtitle(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    SubtitlePath.query.filter(SubtitlePath.uuid == uuid).delete()
    db.session.commit()
    return watchMovie(uuid)


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
