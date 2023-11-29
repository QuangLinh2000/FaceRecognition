from Service.BaseService import BaseService
from models.FaceIdAuth import FaceIdAuth


class FaceIdAuthService(BaseService):
    __instance = None

    def __init__(self):
        super().__init__(FaceIdAuth)
        if FaceIdAuthService.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            FaceIdAuthService.__instance = self

    @staticmethod
    def getInstance():
        if FaceIdAuthService.__instance == None:
            FaceIdAuthService()
        return FaceIdAuthService.__instance

    def getByCardNumber(self, cardNumber):
        session = self.DBSession()
        try:
            return session.query(FaceIdAuth).filter(FaceIdAuth.CardNumber == cardNumber).all()
        except Exception as e:
            return []
        finally:
            session.close()

    def deleteByCardNumber(self, cardNumber):
        session = self.DBSession()
        try:
            session.query(FaceIdAuth).filter(FaceIdAuth.CardNumber == cardNumber).delete()
            session.commit()
            return True
        except Exception as e:
            return False
        finally:
            session.close()
