from django.db import models
from BTBU_query.数据库.const import *
import pymongo
import traceback, sys



# Create your models here.
class MongoConn(object):
    def __init__(self):
        # connect db
        try:
            self.conn = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'])
            self.db = self.conn[MONGODB_CONFIG['db_name']]  # connect db
            self.username = MONGODB_CONFIG['username']
            self.password = MONGODB_CONFIG['password']
            if self.username and self.password:
                self.connected = self.db.authenticate(self.username, self.password)
            else:
                self.connected = True
        except Exception:
            print(traceback.format_exc())
            print('Connect Statics Database Fail.')
            sys.exit(1)