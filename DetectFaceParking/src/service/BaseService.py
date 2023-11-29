from abc import abstractmethod
import logging
from math import ceil

from src.model.Connection import Connection


class BaseService():

    def __init__(self, type=None):
        self.logging = logging

        self.DBSession = Connection.getInstance().DBSession

    def create(self, data):
        session = self.DBSession()
        try:
            session.add(data)
            session.commit()
            session.refresh(data)
            return True
        except Exception as e:
            print(e)
            logging.error("BaseService create table error: " + str(e), exc_info=True)
            session.rollback()
            return False
        finally:
            session.close()

    def update(self, data):
        sessionLocal = self.DBSession()
        try:
            session_data = sessionLocal.merge(data)  # Merge the data into the current session
            sessionLocal.commit()
            sessionLocal.refresh(session_data)
            return True
        except Exception as e:
            print(e)
            logging.error("BaseService update table error: " + str(e), exc_info=True)
            sessionLocal.rollback()
            return False
        finally:
            sessionLocal.close()

    def delete(self, data):
        sessionLocal = self.DBSession()
        try:
            #find by id
            data = sessionLocal.query(data.__class__).filter(data.__class__.ID == data.ID).first()
            session_data= sessionLocal.delete(data)
            sessionLocal.commit()
            if session_data is not None:
                sessionLocal.refresh(session_data)
            return True
        except Exception as e:
            print(e)
            logging.error("BaseService delete table error: " + str(e), exc_info=True)
            sessionLocal.rollback()
            return False
        finally:
            sessionLocal.close()

    def deleteAll(self, Entity):
        session = self.DBSession()
        try:
            session.query(Entity).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logging.error("BaseService deleteAll table error: " + str(e), exc_info=True)
            return False
        finally:
            session.close()

    def deleteByID(self, id, Entity):
        session = self.DBSession()
        try:
            session.query(Entity).filter(Entity.ID == id).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            logging.error("BaseService deleteByID table error: " + str(e), exc_info=True)
            return False
        finally:
            session.close()

    def insertOne(self, data):
        try:
            dataSave = self.convertDataCloud(data)
            res = self.create(dataSave)
            return res
        except Exception as e:
            print(e)
            logging.error("BaseService insertOne table error: " + str(e), exc_info=True)
            return False

    def updateOne(self, data):
        try:
            dataSave = self.convertDataCloud(data)
            res = self.update(dataSave)
            return res
        except Exception as e:
            print(e)
            logging.error("BaseService updateOne table error: " + str(e), exc_info=True)
            return False

    def getAll(self, Entity):
        session = self.DBSession()
        try:
            return session.query(Entity).where(Entity.IsDelete == False).all()
        except Exception as e:
            logging.error("BaseService getAll table error: " + str(e), exc_info=True)
            return []
        finally:
            session.close()

    @abstractmethod
    def custom_filter(self,query,key):
        pass

    def sync(self, list):
        try:
            listInsert = list['ListInsert']
            listUpdate = list['ListUpdate']

            listIdInsert = self.insertList(listInsert)
            listIdUpdate = self.updateList(listUpdate)
            return {'ListInsert': listIdInsert, 'ListUpdate': listIdUpdate}
        except Exception as e:
            logging.error("BaseService sync table error: " + str(e), exc_info=True)
            return {'ListInsert': [], 'ListUpdate': []}

    def insertList(self, list):
        listIdInsert = []
        for dataItem in list:
            try:
                dataSave = self.convertDataCloud(dataItem)
                data = self.getById(dataSave.ID)
                if data is None:
                    res = self.create(dataSave)
                    if res:
                        listIdInsert.append(dataSave.ID)
                else:
                    listIdInsert.append(dataSave.ID)
            except Exception as e:
                logging.error("BaseService insertList table error: " + str(e), exc_info=True)
                print(e)
        return listIdInsert

    def updateList(self, list):
        listIdUpdate = []
        for dataItem in list:
            try:
                dataSave = self.convertDataCloud(dataItem)
                res = self.update(dataSave)
                if res:
                    listIdUpdate.append(dataSave.ID)
            except Exception as e:
                logging.error(e)
                print("BaseService updateList table error: " + str(e), exc_info=True)
        return listIdUpdate

    @abstractmethod
    def convertDataCloud(self, data):
        pass

    @abstractmethod
    def getById(self, id):
        pass
