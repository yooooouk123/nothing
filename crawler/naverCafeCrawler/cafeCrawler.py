__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '5/31/2016'

from datetime import datetime
import time
import os

class CafeCrawler():
    # represent NAVER CAFE crawler

    def __init__(self):
        pass

    def setCnf(self, cnfFile):
        self.cnfDict = dict()
        self.dbCnfDict = dict()
        self.read_conf(cnfFile)
        self.connect_db("./cnf/database.cnf", "./cnf/naver_cafe_schema.sql")

    def read_conf(self, confFile):
        with open(confFile, "r") as f:
            for line in f.readlines():
                if line.strip().strip("\n") != "" and line.startswith("#") is False:
                    elem = line.strip().strip("\n").split("=", 1)
                    if elem[0] in ['query', 'boardURL']:
                        self.cnfDict[elem[0]] = elem[1].strip("\"").split(";")
                    elif elem[0] in ['multi_board']:
                        self.cnfDict[elem[0]] = eval(elem[1])
                    else:
                        self.cnfDict[elem[0]] = elem[1]
        self.cnfDict['retry'] = int(self.cnfDict['retry'])
        if "end_date" not in self.cnfDict.keys():
            self.cnfDict['end_date'] = str(datetime.now().date())
        else:
            self.cnfDict['end_date'] = self.cnfDict['end_date']
        os.environ['TZ'] = self.cnfDict['timeZone']
        time.tzset()
        print("Finish reading configuration file...")

    def connect_db(self, dbConfFile, dbSchemaFile):
        from naverCafeCrawler.mysqlConnector import Mysql
        with open(dbConfFile, "r") as f:
            for line in f.readlines():
                if line.strip().strip("\n") != "" and line.startswith("#") is False:
                    elem = line.strip().strip("\n").split("=", 1)
                    self.dbCnfDict[elem[0]] = elem[1]
        self.dbCnfDict['project'] = self.cnfDict['project']
        self.mysql = Mysql()
        self.mysql.connect_db(self.dbCnfDict, dbSchemaFile)
        print("Finish connecting to database...")

    def start_work(self):
        from naverCafeCrawler.naverCafe import NaverCafe
        c = NaverCafe(self.cnfDict, self.mysql)
        if 'query' in self.cnfDict.keys():
            for query in self.cnfDict['query']:
                print("\nStart searching naver cafe with query '(%s)'..." % query)
                #####################c.search_cafe(query)
                print("\nFinish with query '(%s)'...\n" % query)
                print(str(datetime.now()) + "\n")
                print("=============================")
        else:
            print("\nThere's no query term. Start trying collect all bulletin board...")
            if 'boardURL' not in self.cnfDict.keys():
                print("There must be 'boardURL' information in the main.cnf file. Stop processing...")
            else:
                print("Start searching pos")
                c.search_board()
                print("\nFinish on boardURL...\n")
                print(str(datetime.now()) + "\n")
                print("=============================")
