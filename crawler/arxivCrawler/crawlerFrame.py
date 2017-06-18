__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/18/2016'

import re
import os
from datetime import datetime
import xml.etree.ElementTree as ET
from bs4 import element

class CrawlerFrame():

    def __init__(self, resultPath, db_name):
        self.currentYear = None
        self.resultPath = resultPath
        self.url = "http://arxiv.org/list/cs/%s?skip=%i&show=100"
        self.url_pdf = "http://arxiv.org/pdf/%s.pdf"
        self.url_abs = "http://arxiv.org/abs/%s"
        self.url_api_desc = "http://export.arxiv.org/api/query?id_list=%s"
        self.dbCnfDict = dict()
        self.sql1 = "INSERT IGNORE INTO paper VALUES"
        self.sql2 = "(%s, %s, %s, %s, %s, %s, %s, %s),"
        self.connect_db("./arxivCrawler/database.cnf",
                        "./arxivCrawler/arxiv.sql", db_name)
        from arxivCrawler.requestsHandler import Req
        self.r = Req()
        # temp cnf location(lazy...)

    def connect_db(self, dbConfFile, dbSchemaFile, db_name):
        from arxivCrawler.mysqlConnector import Mysql
        with open(dbConfFile, "r") as f:
            for line in f.readlines():
                if line.strip().strip("\n") != "" and line.startswith("#") is False:
                    elem = line.strip().strip("\n").split("=", 1)
                    self.dbCnfDict[elem[0]] = elem[1]
        self.dbCnfDict['project'] = db_name
        self.mysql = Mysql()
        self.mysql.connect_db(self.dbCnfDict, dbSchemaFile)
        print("Finish connecting to database...")

    def startWork(self, year):
        print("\n%s" % str(datetime.now()))
        self.currentYear = re.search(r"20(\d+)", str(year)).group(1)
        existingFileSet = self.getFileNames(self.resultPath % ("20%s" % self.currentYear))
        print("Get file name list finished...")
        skip = 0
        pages = 1   # initial value
        firstAccess = 1
        while skip < pages:
            value_list = list()
            url = self.url % (self.currentYear, skip)
            err_code, soup = self.r.access_page(url, 4)
            if err_code != 1:       # error
                print(url)
            else:
                if firstAccess == 1:
                    pages = int(re.search(r"total of (\d+) entries", str(soup)).group(1))
                    firstAccess = 0
                else:
                    subject_list = list()
                    for firstSubject in soup.findAll("span", {"class": "primary-subject"}):
                        try:
                            subject_list.append(re.search(r"\((cs\.\D+)\)", firstSubject.text).group(1))
                        except:
                            subject_list.append("pass")
                    idx = 0
                    for idSection in soup.findAll("span", {"class": "list-identifier"}):
                        if subject_list[idx].startswith("cs"):
                            p_id = re.search(r"arXiv:(.+)", idSection.find("a").text).group(1)
                            if "%s.pdf" % p_id.replace("/", "_") not in existingFileSet:
                                if idSection.find("a", attrs={"title": "Download PDF"}) is not None:
                                    var_list = self.getMetadata(p_id)
                                    print("More pdf: %s" % p_id)
                                    self.downloadPdf(p_id)
                                    value_list += ([p_id] + var_list)
                                else:
                                    print("There's no pdf file: %s" % p_id)
                            else:
                                print("Existing pdf file: %s" % p_id)
                        else:
                            print("Not %s category" % self.dbCnfDict['project'])
                        idx += 0
                    sql = self.sql1+(self.sql2*int(len(value_list)/8)).strip(",")
                    self.mysql.insert_mysql(sql, value_list)
                    print("Finish 100 articles...")
                    print(str(datetime.now()))
                    print("============================\n")
                    skip += 100

    def getFileNames(self, path):
        returnSet = list()
        for f in os.listdir(path):
            returnSet.append(f.rstrip(".pdf"))
        returnSet = set(returnSet)
        return returnSet

    def getMetadata(self, p_id):
        err_code, soup = self.r.access_page(self.url_abs % p_id, 4)
        try:    #
            for c in soup.find("h1", {"class": "title mathjax"}).children:
                if type(c) == element.NavigableString:
                    title = c.strip()
        except AttributeError:
            print(soup)
            print(p_id)
            exit()
        dateSection = soup.find("div", {"class": "dateline"}).text
        try:
            dateText = re.search(r"last revised (\d+ \S+ \d+)", dateSection).group(1)
        except AttributeError:
            dateText = re.search(r"Submitted on (\d+ \S+ \d+)", dateSection).group(1)
        date = str(datetime.strptime(dateText, "%d %b %Y")).split(" ")[0]
        author_list = list()
        for a in soup.find("div", {"class": "authors"}).findAll("a"):
            author_list.append(a.text)
        subject_list = soup.find("td", {"class": "tablecell subjects"}).text.split("; ")
        for c in soup.find("blockquote", {"class": "abstract mathjax"}).children:
            if type(c) == element.NavigableString:
                abstract = c.replace("\n", " ").strip()
        return [title, date, author_list[0], ";".join(author_list),
                subject_list[0], ";".join(subject_list), abstract]

    def downloadPdf(self, p_id):
        r_path = self.resultPath % ("20%s" % self.currentYear)
        if not os.path.exists(r_path):
            os.makedirs(r_path)
        err_code, r = self.r.access_page(self.url_pdf % p_id, 4, True)
        if err_code != 1:
            print("error while downloading pdf: %s" % p_id)
        else:
            with open("%s%s.pdf" % (r_path, p_id.replace("/", "_")), 'wb') as pdf:
                for chunk in r.iter_content(10240):
                    pdf.write(chunk)

    def apiRequests(self, year):
        print("\n%s" % str(datetime.now()))
        self.currentYear = re.search(r"20(\d+)", str(year)).group(1)
        existingFileSet = self.getFileNames(self.resultPath % ("20%s" % self.currentYear))
        print("Get file name list finished...")
        sql = "SELECT p_id FROM paper WHERE p_id LIKE 'cs_%s%%' OR p_id LIKE '%s%%';" \
              % (self.currentYear, self.currentYear)
        self.mysql.cur.execute(sql)
        existingIdSet = set()
        for p_id in self.mysql.cur.fetchall():
            existingIdSet.update(p_id)
        print("Fetching mysql p_id set finished...")
        requestIdSet = existingFileSet - existingIdSet
        print("The number of additional id to send request is %i" % len(requestIdSet))
        idx = 0
        for p_id in requestIdSet:
            idx += 1
            if idx % 100 == 0:
                print("%i request finished..." % idx)
                print("%s\n" % str(datetime.now()))
            err_code, r = self.r.access_page(self.url_api_desc % p_id, 4, pdf=True)
            if err_code != 1:
                print("Request error: %s" % p_id)
            else:
                tree = ET.ElementTree(ET.fromstring(r.text))
                var_tuple = (p_id, ) + self.parseXml(tree)
                sql = self.sql1+self.sql2.strip(",")
                self.mysql.insert_mysql(sql, var_tuple)

    def parseXml(self, tree):
        root = tree.getroot()
        ns = {'entry': "{http://www.w3.org/2005/Atom}%s"}
        entry = root.find(ns['entry'] % "entry")
        p_date = entry.find(ns['entry'] % "published").text.split("T")[0]
        p_title = entry.find(ns['entry'] % "title").text.replace("\n", "").strip()
        p_summary = entry.find(ns['entry'] % "summary").text.replace("\n", "").strip()
        author_list = list()
        for a in entry.findall(ns['entry'] % "author"):
            author_list.append(a[0].text)
        subject_list = list()
        for s in entry.findall(ns['entry'] % "category"):
            subject_list.append(s.get('term'))
        return p_title, p_date, author_list[0], ";".join(author_list), \
               subject_list[0], ";".join(subject_list), p_summary
