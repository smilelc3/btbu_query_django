import time
from BTBU_query.database.const import *
from BTBU_query.database.mongoConn import MongoConn

# TODO(liuchang)： 完善自动扫描

class Updater:
    """
    该类实现成绩类的自动更新
    """
    def __init__(self, cycle_s = 300):
        """
        :param cycle_s: 定义扫描周期，默认5min(300s)
        """

        self.collectionID =  MongoConn().db.get_collection(mongoCollections[0])

    def _get_all_id(self):
        """
        获取所有的有效ID
        :return:
        """
        self.collectionID.find()

