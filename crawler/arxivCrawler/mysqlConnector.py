__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/17/2016'

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
                self.cur.execute("SET NAMES utf8")
                break
            except:     # if it fails, create project db and try to connect again
                print("Start creating database...")
                schema = open(dbSchemaFile, "r").read()
                cfg_dict = dict(host=dbCnfDict['host'], usr=dbCnfDict['usr'],
                                pwd=dbCnfDict['pwd'], db='information_schema')
                self.easy_mysql(cfg_dict, encoding=dbCnfDict['encoding'], autocommit=True)
                self.cur.execute("CREATE DATABASE IF NOT EXISTS `%s` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;" % dbCnfDict['project'])
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
            print(varTuple)
