__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '3/27/2016'

from datetime import datetime
import time
import os

class NewsCrawler():
    # represent news crawler

    def __init__(self):
        pass

    def setCnf(self, cnfFile):
        self.cnfDict = dict()
        self.dbCnfDict = dict()
        self.read_conf(cnfFile)
        self.create_regex_dict()
        self.connect_db("./cnf/database.cnf", "./cnf/news_schema.sql")
        self.sectionDict = dict(politics=100, economy=101, society=102, livingCulture=103, world=104,
                           ITScience=105, entertainment=106, photo=107, TV=108)
        self.sectionDictKo = dict(politics='정치', economy='경제', society='사회', livingCulture='생활/문화',
                             world='세계', ITScience='IT/과학', entertainment='연예', photo='포토', TV='TV')

    def read_conf(self, confFile):
        with open(confFile, "r") as f:
            for line in f.readlines():
                if line.strip().strip("\n") != "" and line.startswith("#") is False:
                    elem = line.strip().strip("\n").split("=", 1)
                    if elem[0] in ['query', 'section']:
                        self.cnfDict[elem[0]] = elem[1].split(";")
                    else:
                        self.cnfDict[elem[0]] = elem[1]
        self.cnfDict['retry'] = int(self.cnfDict['retry'])
        if self.cnfDict['comment'] == "True":
            self.cnfDict['comment'] = True
        elif self.cnfDict['comment'] == "False":
            self.cnfDict['comment'] = False
        else:
            print("Please check the 'comment' option in your 'main.cnf' file..")
            exit()
        if "end_date" not in self.cnfDict.keys():
            self.cnfDict['end_date'] = str(datetime.now().date())
        else:
            self.cnfDict['end_date'] = self.cnfDict['end_date']
        os.environ['TZ'] = self.cnfDict['timeZone']
        time.tzset()
        print("Finish reading configuration file...")

    def connect_db(self, dbConfFile, dbSchemaFile):
        from newsCrawler3.mysqlConnector import Mysql
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
        if self.cnfDict['source'] == 'naver':
            from newsCrawler3.naverNews import NaverNews
            c = NaverNews(self.cnfDict, self.mysql, self.re_dict)
        else:
            from newsCrawler3.kindsNews import KindsNews
            c = KindsNews(self.cnfDict, self.mysql, self.re_dict)
        if 'query' in self.cnfDict.keys():
            for query in self.cnfDict['query']:
                print("\nStart searching news(%s) with query '(%s)'..." % (self.cnfDict['source'], query))
                c.search_news(query)
                print("\nFinish with query '(%s)'...\n" % query)
                print(str(datetime.now()) + "\n")
                print("=============================")
        else:
            print("\nThere's no query term. Start trying collect all section...")
            if self.cnfDict['source'] != 'naver':
                print("Collecting all section is only available on Naver news. Stop processing...")
            else:
                if 'section' not in self.cnfDict.keys():
                    print("There must be 'section' information in the main.cnf file. Stop processing...")
                else:
                    for section in self.cnfDict['section']:
                        print("Start searching news on section '(%s)'..." % section)
                        c.search_all_section(section, self.sectionDict, self.sectionDictKo)
                        print("\nFinish on section '(%s)'...\n" % section)
                        print(str(datetime.now()) + "\n")
                        print("=============================")

    def create_regex_dict(self):
        re_dict = dict()
        re_dict["["] = "\["
        re_dict["]"] = "\]"
        re_dict["{"] = "\{"
        re_dict["}"] = "\}"
        re_dict["("] = "\("
        re_dict[")"] = "\)"
        re_dict["*"] = "\*"
        re_dict["+"] = "\+"
        re_dict["?"] = "\?"
        re_dict["^"] = "\^"
        re_dict["$"] = "\$"
        re_dict["#"] = "\#"
        re_dict["‘"] = "\'"
        re_dict["’"] = "\'"
        re_dict["“"] = '\"'
        re_dict["”"] = '\"'
        self.re_dict = re_dict
