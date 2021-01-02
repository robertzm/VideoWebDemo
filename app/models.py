#coding:utf8
from . import db

class DevoUser(db.Model):
    __tablename__ = "devoUser"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))

    def __repr__(self):
        return '<User %r>' % self.username

class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True)
    nameEN = db.Column(db.String(100), unique=True, nullable=True)
    nameCN = db.Column(db.String(100), nullable=True)
    path = db.Column(db.String(100), nullable=True)
    fileName = db.Column(db.String(100), nullable=False)
    short = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return "<Movie {}>".format(self.nameEN)
