from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired, Length


class SeriesPathForm(Form):
    path = StringField('path', default='series', validators=[InputRequired(), Length(max=100)])
    submit = SubmitField('submit')
