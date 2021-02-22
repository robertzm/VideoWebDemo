from flask_wtf import Form, FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length, DataRequired


class SubtitlePathForm(Form):
    path = StringField('path', default='subtitle', validators=[InputRequired(), Length(max=100)])
    submit = SubmitField('submit')


class SubtitleInfoForm(Form):
    lang = SelectField('language', choices=[("Simple-Chinese", "Simple-Chinese"),
                                            ("Traditional-Chinese", "Traditional-Chinese"),
                                            ("English", "English")])
    path = SelectField('path')
    submit = SubmitField('submit')


class SearchForm(FlaskForm):
    search = StringField('search', validators=[DataRequired()])
    submit = SubmitField('Submit')
