import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from src.model.AddModel import addModle
from src.model.Base import Base


class Connection():
    __instance = None

    def __init__(self,host=None):
        if Connection.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            try:
                self.host = os.getenv('HOST_DB')
                self.port = os.getenv('PORT_DB')
                self.database = os.getenv('DATABASE_NAME')
                self.username = os.getenv('USERNAME_DB')
                self.password = os.getenv('PASSWORD_DB')
                Connection.__instance = self
                self.DBSession = None
                self.engine = create_engine(f'mariadb+mariadbconnector://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}')
                Base.metadata.create_all(self.engine)
                self.DBSession = sessionmaker(bind=self.engine)
                # render model have in project
                addModle(self.engine)
            except Exception as e:
                print(e)
    #connect pool

    @staticmethod
    def getInstance(host=None):
        if Connection.__instance == None:
            Connection(host)
        return Connection.__instance
