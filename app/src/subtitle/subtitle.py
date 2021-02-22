# Blueprint Configuration
import os, sys

from flask import Blueprint, url_for, render_template, make_response
from flask_login import current_user
from werkzeug.utils import redirect

from app import db
from app.src.subtitle.forms import SubtitlePathForm, SubtitleInfoForm
from app.src.subtitle.models import SubtitlePath
from app.src.util.files import secureAndAddFile, addSubtitle

subtitle_bp = Blueprint(
    "subtitle_bp", __name__, template_folder="templates", static_folder="static"
)


@subtitle_bp.route("/addSubtitle", methods=['GET', 'POST'])
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


@subtitle_bp.route("/link/<uuid>", methods=['GET', 'POST'])
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
        from app.src.movie.movie import watchMovie
        return watchMovie(uuid)
    return render_template("home/editSubtitle.html", uuid=uuid, form=form)


@subtitle_bp.route("/delete/<uuid>", methods=['GET', 'POST'])
def deleteSubtitle(uuid):
    if not current_user.is_authenticated:
        return redirect(url_for('user_bp.loginUser'))
    SubtitlePath.query.filter(SubtitlePath.uuid == uuid).delete()
    db.session.commit()
    from app.src.movie.movie import watchMovie
    return watchMovie(uuid)
