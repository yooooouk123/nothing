__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/10/2016'

from newsCrawler3.newsCrawler import NewsCrawler


class KindsNews(NewsCrawler):
    # represent KINDS news crawler

    def __init__(self, cnfDict, dbConnection, re_dict):
        NewsCrawler.__init__(self)
        self.cnfDict = cnfDict
        self.mysql = dbConnection
        self.re_dict = re_dict

    def search_news(self):
        pass
