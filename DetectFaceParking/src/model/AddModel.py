from src.model.FaceIdAuth import FaceIdAuth


def addModle(engine):
    FaceIdAuth.__table__.create(bind=engine, checkfirst=True)
