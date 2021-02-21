import os, shortuuid, uuid
import re

from werkzeug.utils import secure_filename

from app import db
from app.models import Series, SubtitlePath
from app.src.movie.models import MoviePath, MovieInfoV3


def secureAndAddFile(dir: str, uid: str, addMethod):
    files = os.listdir(dir)
    for file in files:
        filepath = os.path.join(dir, file)
        if os.path.isdir(filepath):
            secureAndAddFile(filepath, uid, addMethod)
        elif file.startswith('.'):
            pass
        else:
            sf = secure_filename(file)
            newFile = os.path.join(dir, sf)
            if not newFile.__eq__(filepath):
                os.rename(filepath, newFile)
            addMethod(newFile, uid)


def addMovie(filepath: str, uid: str) -> None:
    absPath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = MoviePath.query.filter(MoviePath.filepath == absPath).first()
    if not existing:
        uid = shortuuid.encode(uuid.uuid1())
        record = MoviePath(uuid=uid, filepath=absPath)
        info = MovieInfoV3(uuid=uid)
        db.session.add(record)
        db.session.add(info)
        db.session.commit()


def addSeries(filepath: str, uid: str) -> None:
    relativePath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = Series.query.filter(Series.filepath == relativePath).first()
    tmp = re.search('\.(S[0-9]*)?E[0-9]*\.', relativePath.upper())
    if tmp:
        episode = tmp[0][1:-1]
    else:
        episode = 'NONE'
    if not existing:
        e = Series(uuid=uid, episode=episode, filepath=relativePath)
        db.session.add(e)
        db.session.commit()


def addSubtitle(filepath: str, uid: str) -> None:
    absPath = filepath.split('static')[1].replace('\\', '/')[1:]
    existing = SubtitlePath.query.filter(SubtitlePath.filepath == absPath).first()
    if not existing:
        record = SubtitlePath(filepath=absPath)
        db.session.add(record)
        db.session.commit()
