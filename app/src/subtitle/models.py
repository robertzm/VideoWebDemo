from app import db


class SubtitlePath(db.Model):
    __tablename__ = "subtitle"
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(64), unique=True, nullable=True)
    lang = db.Column(db.String(32))
    filepath = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return "<Subtitle path {}>".format(self.filepath)
