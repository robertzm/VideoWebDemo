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

    def filePath(self):
        return self.fileName if self.path == None else self.path + '/' + self.fileName

class MoviePath(db.Model):
    __tablename__ = "MoviePath"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, nullable=False)
    filepath = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return "<Movie Path {}".format(self.filepath)

    def file(self):
        # the replace() is only for windows sys
        return str(self.filepath).split('static')[1].replace('\\', '/')

class MovieInfo(db.Model):
    __tablename__ = "MovieInfo"
    uuid = db.Column(db.String(64), primary_key=True, nullable=False)
    nameen = db.Column(db.String(128), nullable=True)
    namecn = db.Column(db.String(128), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    director = db.Column(db.String(128), nullable=True)

    def __repr__(self):
        return "<Movie {}".format(self.nameen + "." + self.year)
