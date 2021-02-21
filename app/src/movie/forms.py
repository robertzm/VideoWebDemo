from flask_wtf import Form
from wtforms import StringField, SubmitField, IntegerField, DecimalField
from wtforms.validators import InputRequired, Length, NumberRange


class MoviePathForm(Form):
    path = StringField('path', default='movie', validators=[InputRequired(), Length(max=100)])
    submit = SubmitField('submit')


class MovieInfoForm(Form):
    nameEN = StringField('name-en', validators=[InputRequired(), Length(max=128)])
    nameCN = StringField('name-cn', validators=[Length(max=128)])
    year = IntegerField('year', default=1900, validators=[NumberRange(min=1900, max=2100)])
    director = StringField('director', validators=[Length(max=128)])
    actor = StringField('actor', validators=[Length(max=128)])
    imdb = DecimalField('IMDB', default=0, validators=[NumberRange(min=0, max=10)])
    douban = DecimalField('DouBan', default=0, validators=[NumberRange(min=0, max=10)])
    genre = StringField('Genre', validators=[Length(max=128)])
    comment = StringField('Comment')
    submit = SubmitField('submit')
