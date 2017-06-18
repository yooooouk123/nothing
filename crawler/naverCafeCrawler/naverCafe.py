__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '5/31/2016'

import re
import time
from datetime import datetime
import json
import math
import html
from bs4 import element
from naverCafeCrawler.ndrive import Ndrive
from naverCafeCrawler.cafeCrawler import CafeCrawler
from naverCafeCrawler.requestsHandler import Req

class NaverCafe(CafeCrawler):
    # represent NAVER CAFE crawler

    def __init__(self, cnfDict, dbConnection):
        CafeCrawler.__init__(self)
        self.cnfDict = cnfDict
        self.mysql = dbConnection
        self.nd = Ndrive(self.cnfDict['naverid'], self.cnfDict['naverpw'])
        self.r = Req(self.nd)
        self.main_url = "http://m.cafe.naver.com%s"
        self.board_id_list = list()
        self.board_url_list = list()
        self.board_url = self.main_url % "/ArticleList.nhn?search.clubid=%s&search.menuid=%s&search.boardtype=L"
        self.board_request_url = self.main_url % "/ArticleListAjax.nhn?&search.clubid=%s&search.menuid=%s&search.page=%i"
        self.article_request_url = self.main_url % "/ArticleRead.nhn?clubid=%s&page=1&articleid=%s"
        self.comment_request_url = "http://cafe.naver.com/CommentView.nhn?search.clubid=%s&search.menuid=%s&search.articleid=%s&search.page=%i"
        self.min_article_id = int(self.cnfDict['min_article_id'])
        self.min_article_id_list = list()
        self.stop = False
        self.start_date = datetime.strptime(self.cnfDict['start_date']+" 00:00", "%Y-%m-%d %H:%M")
        self.end_date = datetime.strptime(self.cnfDict['end_date']+" 23:59", "%Y-%m-%d %H:%M")

    def get_comment(self, article_id, board_id):
        page = 1
        err_no, res = self.r.access_page(self.comment_request_url % (self.cafe_id, board_id, article_id, page),
                                          self.cnfDict['retry'], isSoup=False)
        if err_no != 1:
            print("Error comment id: %s" % article_id)
        else:
            c_cnt = 0
            sql_value_part = "(%s, %s, %s, %s, %s, %s, %s, %s, %s),"
            value_tuple = tuple()
            j = json.loads(res.strip())
            total_cnt = j['result']['totalCount']
            if total_cnt == 0:
                print("There's no comment...pass...(%s)" % article_id)
            else:
                while page <= math.ceil(total_cnt/100):
                    for c in j['result']['list']:
                        c_id = c['commentid']
                        c_m_id = c['writerid']
                        c_m_nick = c['writernick']
                        c_datetime_str =c['writedt']
                        if c_datetime_str == "":
                            continue
                        else:
                            c_datetime = datetime.strptime(c_datetime_str, "%Y.%m.%d. %H:%M")
                            c_body = html.unescape(c['content']).replace("<br />", " ")
                            ref_c_id =c['refcommentid']
                            if ref_c_id == c_id:
                                ref_c_id = None
                            value_tuple += (self.cafe_id, board_id, article_id, c_id, c_datetime,
                                            c_m_id, c_m_nick, c_body, ref_c_id)
                            c_cnt += 1
                    page += 1
                self.mysql.insert_comments((sql_value_part*c_cnt).strip(","), value_tuple)

    def get_article(self, url_list):
        idx = 0
        for u in url_list:
            article_id = re.search(r"articleid=(\d+)", u).group(1)
            err_no, soup = self.r.access_page(self.main_url % u, self.cnfDict['retry'])
            if err_no != 1:
                print("Error article url: %s" % u)
            else:
                title_part = soup.find("div", {"class": "post_title"})
                try:
                    menuid = re.search(r"&search\.menuid=(\d+)", title_part.find("a", {"class": "tit_menu"})['href']).group(1)
                except AttributeError:
                    # not valid article
                    continue
                a_datetime_str = title_part.find("span", {"class": "date font_l"}).text
                # 2016.06.07. 15:04
                a_datetime = datetime.strptime(a_datetime_str, "%Y.%m.%d. %H:%M")
                a_title = title_part.find("h2").text.strip()
                if a_datetime > self.end_date:
                    print("After end date range... skip...")
                    print("Title: %s, (%s)" % (a_title, str(a_datetime_str)))
                else:
                    if a_datetime < self.start_date or int(article_id) < self.min_article_id:
                        self.stop = True
                        print("Stop at %s" % a_datetime_str)
                        print("Title: %s" % a_title)
                        break
                    else:
                        m_id = re.search(r"&memberId=(.+)", title_part.find("a", {"class": "nick"})['href']).group(1)
                        m_nick = re.search(r"(.+)\(.+\)", title_part.find("a", {"class": "nick"}).text).group(1)
                        view_cnt = int(title_part.find("span", {"class": "no font_l"}).find("em").text)
                        a_body = html.unescape(self.get_body(soup.find("div", {"id": "postContent"})))
                        self.mysql.insert_article((self.cafe_id, menuid, article_id,
                                                   a_title, a_datetime, m_id, m_nick, view_cnt, a_body))
                        self.get_comment(article_id, menuid)
                        idx += 1
                        time.sleep(0.5)
            self.min_article_id = int(article_id)
        print("Finish %i articles..." % idx)

    def get_article2(self, article_id):
        return_value = False
        err_no, soup = self.r.access_page(self.article_request_url%(self.cafe_id, article_id),
                                  self.cnfDict['retry'])
        if err_no != 1:
            print("Error article id: %s" % article_id)
        else:
            title_part = soup.find("div", {"class": "post_title"})
            try:
                menuid = re.search(r"&search\.menuid=(\d+)", title_part.find("a", {"class": "tit_menu"})['href']).group(1)
            except AttributeError:
                # not valid article
                self.min_article_id = int(article_id)
                return False
            if menuid in self.board_id_list:
                a_datetime_str = title_part.find("span", {"class": "date font_l"}).text
                # 2016.06.07. 15:04
                a_datetime = datetime.strptime(a_datetime_str, "%Y.%m.%d. %H:%M")
                a_title = title_part.find("h2").text.strip()
                if a_datetime > self.end_date:
                    print("After end date range... skip...")
                    print("Title: %s, (%s)" % (a_title, str(a_datetime_str)))
                else:
                    if a_datetime < self.start_date or article_id < self.min_article_id:
                        self.stop = True
                        print("Stop at %s" % a_datetime_str)
                        print("Title: %s" % a_title)
                    else:
                        m_id = re.search(r"&memberId=(.+)", title_part.find("a", {"class": "nick"})['href']).group(1)
                        m_nick = re.search(r"(.+)\(.+\)", title_part.find("a", {"class": "nick"}).text).group(1)
                        view_cnt = int(title_part.find("span", {"class": "no font_l"}).find("em").text)
                        a_body = html.unescape(self.get_body(soup.find("div", {"id": "postContent"})))
                        self.mysql.insert_article((self.cafe_id, menuid, article_id,
                                                   a_title, a_datetime, m_id, m_nick, view_cnt, a_body))
                        self.get_comment(article_id, menuid)
                        return_value = True
        self.min_article_id = int(article_id)
        time.sleep(1)
        return return_value

    def recursive(self, bodyList, tree):
        for c in tree.children:
            if type(c) == element.Comment:
                pass
            elif type(c) == element.NavigableString:
                if c == '\xa0':
                    pass
                else:
                    bodyList.append(c)
            elif c.name == 'br':
                bodyList.append(' ')
            else:
                bodyList = self.recursive(bodyList, c)
        return bodyList

    def get_body(self, body_part):
        return_list = list()
        return_list = self.recursive(return_list, body_part)
        return_string = " ".join(return_list).strip()
        return re.sub(r"\s+", " ", return_string)

    def search_board(self):
        print("Start searching cafe board...")
        print(datetime.now())
        for url in self.cnfDict['boardURL']:
            self.cafe_id = re.search(r"search\.clubid=(\d+)&", url).group(1)
            b_id = re.search(r"search\.menuid=(\d+)&", url).group(1)
            self.board_id_list.append(b_id)
            b_url = self.board_url % (self.cafe_id, b_id)
            self.board_url_list.append(b_url)
            err_no, soup = self.r.access_page(b_url, self.cnfDict['retry']+2)
            if err_no != 1:
                print("Error(from the start)...Stop...")
                exit()
            else:
                cafe_title = soup.find("title").text.strip()
                cafe_name = self.cnfDict['cafeURL'].rsplit("/", 1)[1]
                board_name = soup.find("meta", {"name":"menuName"})['content'].strip()
                # insert cafe and board info into DB
                self.mysql.insert_cafe(cafe_id=self.cafe_id, cafe_name=cafe_name, cafe_title=cafe_title)
                self.mysql.insert_board(cafe_id=self.cafe_id, board_id=b_id, board_name=board_name)
        # start main process
        ar_idx = 1
        url_idx = 0
        while url_idx < len(self.board_url_list):
            print("Start retrieving articles in the board id %s..." % self.board_id_list[url_idx])
            page_idx = 1
            url_list = list()
            while page_idx <= 1000:
                err_no, soup = self.r.access_page(self.board_request_url %
                                                  (self.cafe_id, self.board_id_list[url_idx], page_idx),
                                                  self.cnfDict['retry']+1)
                if err_no != 1:
                    print("Error page %i....Skip the page..." % page_idx)
                else:
                    for li in soup.find_all("li"):
                        url_list.append(li.find("a", {"class": "link_item"})['href'])
                        ar_idx += 1
                    if url_list == []:          # there's no 1000 pages
                        print("There's no more posts...")
                        break
                    if page_idx % 10 == 0:
                        self.get_article(url_list)
                        url_list = list()
                        time.sleep(1)
                    if self.stop is True:           # in 1000 page , over date range
                        self.stop = False
                        break
                page_idx += 1
            self.min_article_id_list.append(self.min_article_id)
            print("Finish retrieving articles in the board id %s...Start retrieving additional articles..." %
                  self.board_id_list[url_idx])
            print(datetime.now())
            url_idx += 1

        if self.cnfDict['multi_board'] is True:
            print(self.min_article_id_list)
            self.min_article_id = max(self.min_article_id_list)
        if self.stop is False:
            ch = 0
            while True:
                if ch % 500 == 0 and ch != 0:
                    print("current...: %i" % self.min_article_id)
                    print(datetime.now())
                    time.sleep(5)
                if self.stop is True:
                    print("The number of article: %i... Finished..." % ar_idx)
                    print(datetime.now())
                    break
                isOkay = self.get_article2(self.min_article_id - 1)
                ch += 1
                if isOkay is True:
                    ar_idx += 1

