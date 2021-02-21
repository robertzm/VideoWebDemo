# coding:utf8
from . import db


class SubtitlePath(db.Model):
    __tablename__ = "subtitle"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, nullable=True)
    lang = db.Column(db.String(32))
    filepath = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return "<Subtitle path {}>".format(self.filepath)


class Series(db.Model):
    __tablename__ = "series"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), nullable=False)
    episode = db.Column(db.String(32), nullable=True)
    filepath = db.Column(db.String(256), nullable=False)
    subtitle = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return "<Series {}>".format(self.name)
