# Blueprint Configuration
import re

from flask import Blueprint, url_for, render_template, request
from flask_login import current_user
from sqlalchemy import asc, desc
from werkzeug.utils import redirect

from app.src.base.forms import SearchForm
from app.src.movie.models import MovieInfoV3

base_bp = Blueprint(
    "base_bp", __name__, template_folder="templates", static_folder="static"
)

@base_bp.route("/", methods=["GET", "POST"])
def home():
    return list()


@base_bp.route('/list', methods=['GET', 'POST'])
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
