import os, shortuuid, uuid

from app.models import Series


def getOrCreateUUID(dir: str) -> (bool, str):
    files = os.listdir(dir)
    files = [os.path.join(dir, f).split('static')[1].replace('\\', '/')[1:] for f in files]
    allSeries = Series.query.all()
    for episode in allSeries:
        if episode.filepath in files:
            return (True, episode.uuid)
    return (False, shortuuid.encode(uuid.uuid1()))
