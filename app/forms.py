from flask_wtf import Form
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import InputRequired, Length

class RegisterForm(Form):
  nameEN = StringField('name-en', validators=[InputRequired(), Length(max=100)])
  nameCN = StringField('name-cn', validators=[Length(max=100)])
  path = StringField('path', validators=[Length(max=100)])
  short = StringField('shortname', validators=[InputRequired(), Length(max=20)])
  file = FileField('file', validators=[Length(max=100)])
  submit = SubmitField('submit')