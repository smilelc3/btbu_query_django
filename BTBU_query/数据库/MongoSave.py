"""
数据库存储类
"""
from BTBU_query.数据库.const import *
from BTBU_query.数据库.mongoConn import MongoConn
from BTBU_query.数据库.randomPWBuilder import prpcrypt
from BTBU_query.数据库.one_item import oneItem

class MongoSaveLogin(MongoConn):
    def __init__(self, AES:prpcrypt  = prpcrypt("liuchangliuchang")):
        MongoConn.__init__(self)
        self.AES = AES

    def updateOnePerson(self, persondata:dict, collection = mongoCollections[0]):
        """

        :param persondata:{"studentID":str, "password":str, "acceptAgreement": True/False, "openID":str}
        :param collections:
        :return:
        """
        neededKey = ['studentID']

        self.db.get_collection(collection).update_one({k:v for k,v in persondata.items() if k in neededKey},  {'$set': persondata}, upsert=True)

    def updateOneVerify(self, VerifyCodeData:dict, collections = mongoCollections[1]):

        neededKey = ['ImgPath', 'ImgName', 'Decode', 'CteatedTime']
        self.db.get_collection(collections).update_one({k: v for k, v in VerifyCodeData.items() if k in neededKey},
                                                       {'$set': VerifyCodeData}, upsert=True)

    def updateOneItem(self, oneItem: oneItem, collections = mongoCollections[2]):
        collection = self.db.get_collection(collections)
        collection.update({'课程编号': oneItem.DateDict['课程编号']}, {'$set': oneItem.DateDict}, upsert=True)