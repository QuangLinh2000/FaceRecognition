from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.AddModel import addModle
from models.Base import Base


class Connection():
    __instance = None

    def __init__(self, host=None):
        if Connection.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            try:

                Connection.__instance = self
                self.DBSession = None
                self.engine = create_engine(f'mariadb+mariadbconnector://admin:123456@192.168.103.96:3306/parking')
                Base.metadata.create_all(self.engine)
                self.DBSession = sessionmaker(bind=self.engine)
                # render model have in project
                addModle(self.engine)
            except Exception as e:
                print(e)

    # connect pool

    @staticmethod
    def getInstance(host=None):
        if Connection.__instance == None:
            Connection(host)
        return Connection.__instance
