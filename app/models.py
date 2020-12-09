#coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@127.0.0.1:8889/videoDevo"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

class DevoUser(db.Model):
    __tablename__ = "devoUser"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))

    def __repr__(self):
        return '<User %r>' % self.username

if __name__ == "__main__":
    db.create_all()
    admin = DevoUser(id = 1, username = 'zibomeng', pwd = '12345678')
    guest = DevoUser(id = 2, username = 'yingri', pwd = '11111111')

    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()

    print(DevoUser.query.all())
    print(DevoUser.query.filter_by(username='zibomeng').first())

    db.session.delete(DevoUser.query.filter_by(username='zibomeng').first())
    db.session.delete(DevoUser.query.filter_by(username='yingri').first())
    db.session.commit()

    db.drop_all()
