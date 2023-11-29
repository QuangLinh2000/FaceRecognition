from src.model.FaceIdAuth import FaceIdAuth
from src.service.BaseService import BaseService


class FaceIdAuthService(BaseService):
    def getByName(self, name):
        session = self.DBSession()

        try:
            return session.query(FaceIdAuth).filter(FaceIdAuth.name == name).first()
        except Exception as e:
            self.logging.error("FaceIdAuthService getByName " + str(e), exc_info=True)
            return None
        finally:
            session.close()
