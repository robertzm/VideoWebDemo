from flask_wtf import Form
from wtforms import StringField, SubmitField, FileField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange

class RegisterForm(Form):
  nameEN = StringField('name-en', validators=[InputRequired(), Length(max=100)])
  nameCN = StringField('name-cn', validators=[Length(max=100)])
  path = StringField('path', default='movie', validators=[Length(max=100)])
  short = StringField('shortname', validators=[InputRequired(), Length(max=20)])
  file = FileField('file', validators=[Length(max=100)])
  submit = SubmitField('submit')

class MoviePathForm(Form):
  path = StringField('path', default='movie', validators=[InputRequired(), Length(max=100)])
  submit = SubmitField('submit')

class MovieInfoForm(Form):
  nameEN = StringField('name-en', validators=[InputRequired(), Length(max=128)])
  nameCN = StringField('name-cn', validators=[Length(max=128)])
  year = IntegerField('year', default=1900, validators=[NumberRange(min=1900, max=2100)])
  director = StringField('director', validators=[Length(max=128)])
  submit = SubmitField('submit')
