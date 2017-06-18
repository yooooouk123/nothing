__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/6/2016'

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

    def check_inserted_or_not(self, url):
        sql = "SELECT * FROM url WHERE a_url = '%s';" % url
        row_count = self.cur.execute(sql)
        if row_count == 0:
            # not yet inserted
            return 0, (0,)
        else:
            # already inserted
            row = self.cur.fetchall()
            return 1, row[0]

    def insert_srch_query(self, query, a_id):
        sql = "INSERT IGNORE INTO srch_query VALUE(%s, %s);"
        self.insert_mysql(sql, (query, a_id))

    def update_rel_article(self, mother_id, child_id):
        try:
            sql = "UPDATE article SET rel_id = %i WHERE a_id = %i;" % (mother_id, child_id)
            self.cur.execute(sql)
        except Exception as e:
            print(e)
            print("child id: %s" % str(child_id))

    def insert_url_n_srch_query(self, query, url, res_code):
        if res_code == 1:
            sql = "INSERT INTO url(a_url) VALUE(%s);"
            self.insert_mysql(sql, url)
        else:
            sql = "INSERT INTO url(a_url, err_code) VALUE(%s, %s);"
            self.insert_mysql(sql, (url, res_code))
        check = self.check_inserted_or_not(url)
        self.insert_srch_query(query, check[1][0])
        return check[1][0]

    def insert_news(self, var_tuple, source="naver"):
        sql = "INSERT INTO article(a_id, source, a_press, a_title, a_body, a_datetime, a_cat, isNaver, r_datetime) VALUE(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        err_return = self.insert_mysql(sql, var_tuple)
        if err_return is not None:
            mysql_err, err_query = err_return
            if mysql_err == 1064:
                var_tuple = var_tuple[0:3] + (var_tuple[3],) + var_tuple[4:]
                mysql_err = self.insert_mysql(sql, var_tuple)
                if mysql_err is not None:
                    print(err_query)
                    print(mysql_err)
                    exit()

    def insert_comment(self, var_sql, var_tuple):
        sql = "INSERT INTO comments(a_id, c_num, maskUserId, encodedUserId, c_datetime, c_body, badCnt, goodCnt, likeCnt, replyCnt, fromType, snsType, isBest, c_grade, c_pnt, c_nextGradePnt) VALUES" + var_sql
        self.insert_mysql(sql, var_tuple)

    def update_error_code(self, a_id, res_code):
        sql = "UPDATE url SET err_code = %s WHERE a_id = %s;"
        self.cur.execute(sql, (res_code, a_id))

    def insert_url(self, url):
        sql = "INSERT INTO url(a_url) VALUE(%s);"
        self.insert_mysql(sql, (url,))
        check = self.check_inserted_or_not(url)
        return check[1][0]      # a_id

