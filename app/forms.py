from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField, FileField, IntegerField, PasswordField, BooleanField, SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Length, NumberRange, DataRequired, Email, EqualTo, ValidationError
from app.models import User, InvitationCode


class MoviePathForm(Form):
    path = StringField('path', default='movie', validators=[InputRequired(), Length(max=100)])
    submit = SubmitField('submit')


class SubtitlePathForm(Form):
    path = StringField('path', default='subtitle', validators=[InputRequired(), Length(max=100)])
    submit = SubmitField('submit')


class MovieInfoForm(Form):
    nameEN = StringField('name-en', validators=[InputRequired(), Length(max=128)])
    nameCN = StringField('name-cn', validators=[Length(max=128)])
    year = IntegerField('year', default=1900, validators=[NumberRange(min=1900, max=2100)])
    director = StringField('director', validators=[Length(max=128)])
    submit = SubmitField('submit')


class SubtitleInfoForm(Form):
    lang = SelectField('language', choices=[("Simple-Chinese", "Simple-Chinese"),
                                            ("Traditional-Chinese", "Traditional-Chinese"),
                                            ("English", "English")])
    path = SelectField('path')
    submit = SubmitField('submit')


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    invitationCode = StringField('InvitationCode', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_invitationCode(self, invitationCode):
        record = InvitationCode.query.filter_by(uuid=invitationCode.data).first()
        if record is None or record.used == True:
            raise ValidationError('InvitationCode invalid, please use another one. ')
