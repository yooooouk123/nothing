__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '5/31/2016'

import time
import pymysql


class Mysql():
    # represent mysql connector

    def __init__(self):
        pass

    def connect_db(self, dbCnfDict, dbSchemaFile):
        while True:
            try:        # try to connect to project db
                cfg_dict = dict(host=dbCnfDict['host'], usr=dbCnfDict['usr'],
                                pwd=dbCnfDict['pwd'], db=dbCnfDict['project'])
                self.easy_mysql(cfg_dict, encoding=dbCnfDict['encoding'], autocommit=True)       # turn-on autocummit, be careful!
                self.cur.execute("SET NAMES utf8mb4")
                break
            except:     # if it fails, create project db and try to connect again
                print("Start creating database...")
                schema = open(dbSchemaFile, "r").read()
                cfg_dict = dict(host=dbCnfDict['host'], usr=dbCnfDict['usr'],
                                pwd=dbCnfDict['pwd'], db='information_schema')
                self.easy_mysql(cfg_dict, encoding=dbCnfDict['encoding'], autocommit=True)
                self.cur.execute("CREATE DATABASE IF NOT EXISTS `%s` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */;" % dbCnfDict['project'])
                self.cur.execute(schema % (dbCnfDict['project'], dbCnfDict['project']))        # use project db and create tables
                time.sleep(8)

    def easy_mysql(self, cfg_dict, encoding='utf8', autocommit=False):
        self.con = pymysql.connect(host=cfg_dict['host'], user=cfg_dict['usr'],
                                   passwd=cfg_dict['pwd'], db=cfg_dict['db'], charset=encoding)
        self.cur = self.con.cursor()
        if autocommit is True:
            self.con.autocommit(True)

    def insert_mysql(self, sql, varTuple):
        try:
            self.cur.execute(sql, varTuple)
        except pymysql.Error as e:
            print(e)

    def insert_cafe(self, cafe_id, cafe_name, cafe_title):
        sql = "INSERT INTO cafe VALUE(%s, %s, %s);"
        self.insert_mysql(sql, (cafe_id, cafe_name, cafe_title))

    def insert_board(self, cafe_id, board_id, board_name):
        sql = "INSERT INTO board VALUE(%s, %s, %s);"
        self.insert_mysql(sql, (cafe_id, board_id, board_name))

    def insert_article(self, var_tuple):
        sql = "INSERT INTO article VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        self.insert_mysql(sql, var_tuple)

    def insert_comments(self, sql_value_part, var_tuple):
        sql = "INSERT IGNORE INTO comments VALUES %s;" % sql_value_part
        self.insert_mysql(sql, var_tuple)