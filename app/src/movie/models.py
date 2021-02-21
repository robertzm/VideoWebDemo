from app import db


class MoviePath(db.Model):
    __tablename__ = "moviepath"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, nullable=False)
    filepath = db.Column(db.String(256), nullable=False)

    def __repr__(self):
        return "<Movie Path {}".format(self.filepath)


class MovieInfoV3(db.Model):
    __tablename__ = "movieinfov3"
    uuid = db.Column(db.String(64), primary_key=True, nullable=False)
    nameen = db.Column(db.String(128), nullable=True)
    namecn = db.Column(db.String(128), nullable=True)
    year = db.Column(db.Integer, default=1900, nullable=True)
    director = db.Column(db.String(128), nullable=True)
    actor = db.Column(db.String(128), nullable=True)
    imdb = db.Column(db.Float, default=0, nullable=True)
    douban = db.Column(db.Float, default=0, nullable=True)
    genre = db.Column(db.String(128), nullable=True)
    comment = db.Column(db.String(512), nullable=True)
    isSeries = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(1024), nullable=True)

    def __repr__(self):
        return "<Movie {}".format(self.nameen + "." + self.year)

