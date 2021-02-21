# Blueprint Configuration
from flask import Blueprint, flash, url_for, render_template
from flask_login import current_user, login_user, logout_user
from werkzeug.utils import redirect
import shortuuid, uuid

from app import db
from app.src.user.forms import LoginForm, RegistrationForm
from app.src.user.models import User, InvitationCode

user_bp = Blueprint(
    "user_bp", __name__, template_folder="templates", static_folder="static"
)


@user_bp.route("/login", methods=['GET', 'POST'])
def loginUser():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('user_bp.loginUser'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('home'))
    return render_template('home/login.html', title='Sign In', form=form)


@user_bp.route('/logout')
def logoutUser():
    logout_user()
    return redirect(url_for('user_bp.loginUser'))


@user_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('user_bp.loginUser'))
    return render_template('home/register.html', title='Register', form=form)


@user_bp.route('/generateCode', methods=['GET'])
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
