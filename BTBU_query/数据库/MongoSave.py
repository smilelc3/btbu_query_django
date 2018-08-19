"""
数据库存储类
"""
from BTBU_query.数据库.const import *
from BTBU_query.数据库.mongoConn import MongoConn
from BTBU_query.内网查询.gradeOneItem import gradeOneItem

class MongoSaveLogin(MongoConn):
    def __init__(self):
        MongoConn.__init__(self)

    def updateOnePerson(self, persondata:dict, collection = mongoCollections[0]):
        """

        :param persondata:{"studentID":str, "password":str, "acceptAgreement": True/False, "openID":str}
        :param collections:
        :return:
        """
        neededKey = ['studentID']   # 只需要studentID作为唯一性标示

        self.db.get_collection(collection).update_one({k:v for k,v in persondata.items() if k in neededKey},  {'$set': persondata}, upsert=True)

    # 更新验证码数据
    def updateOneVerify(self, VerifyCodeData:dict, collections = mongoCollections[1]):

        neededKey = ['ImgPath', 'ImgName', 'Decode', 'CteatedTime']
        self.db.get_collection(collections).update_one({k: v for k, v in VerifyCodeData.items() if k in neededKey},
                                                       {'$set': VerifyCodeData}, upsert=True)

    #
    def updateOneItem(self, oneItem: gradeOneItem, collections = mongoCollections[2]):
        collection = self.db.get_collection(collections)
        print(oneItem.DateDict)
        collection.update_one({'课程编号': oneItem.DateDict['课程编号']}, {'$set': oneItem.DateDict}, upsert=True)