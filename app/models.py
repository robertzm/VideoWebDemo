# coding:utf8
from . import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self) -> str:
        return '<User: {}>'.format(self.username)

    def set_password(self, password) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password) -> bool:
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class DevoUser(db.Model):
    __tablename__ = "devoUser"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))

    def __repr__(self):
        return '<User %r>' % self.username


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
