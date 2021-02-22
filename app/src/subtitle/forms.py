from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import InputRequired, Length


class SubtitlePathForm(Form):
    path = StringField('path', default='subtitle', validators=[InputRequired(), Length(max=100)])
    submit = SubmitField('submit')


class SubtitleInfoForm(Form):
    lang = SelectField('language', choices=[("Simple-Chinese", "Simple-Chinese"),
                                            ("Traditional-Chinese", "Traditional-Chinese"),
                                            ("English", "English")])
    path = SelectField('path')
    submit = SubmitField('submit')
