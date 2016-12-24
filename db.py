# -*- coding: utf-8 -*-
import pymysql
from db_lib.db_restaurant import db_restaurant
from db_lib.db_similarity import db_similarity
from db_lib.db_user import db_user
from db_lib.db_tag import db_tag
from db_lib.db_weight import db_weight

class DBConn(db_restaurant, db_similarity, db_user, db_tag, db_weight):
    def __init__(self):
        self.host = '52.78.68.151'
        self.user = 'dbm'
        self.passwd = '5j0 wu654yji4'
        self.dbname = 'warofdata'

    def open(self):
        self.db = pymysql.connect(self.host, self.user, self.passwd, self.dbname, charset='utf8')
        self.db.autocommit(True)
        self.cursor = self.db.cursor()
        self.cursor.execute("SET TIME_ZONE = '+08:00'")

    def close(self):
        self.cursor.close()
        self.db.close()