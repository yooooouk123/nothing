__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/6/2016'

import math
import re
import json
import time
from datetime import datetime, timedelta
from newsCrawler3.newsCrawler import NewsCrawler
from newsCrawler3.requestsHandler import Req


class NaverNews(NewsCrawler):
    # represent Naver news crawler

    def __init__(self, cnfDict, dbConnection, re_dict):
        NewsCrawler.__init__(self)
        self.cnfDict = cnfDict
        self.mysql = dbConnection
        self.re_dict = re_dict
        self.r = Req()
        self.url_format = "http://news.naver.com/main/main.nhn?mode=LSD&mid=shm&sid1=%i#&date=%s 00:00:00&page=%i"
        self.post_url_format = "http://news.naver.com/main/mainNews.nhn?componentId=%i&date=%s 00:00:00&page=%i"
        self.news_url_format = "http://news.naver.com/main/read.nhn?mode=LSD&mid=shm&sid1=%i&oid=%s&aid=%s"

    def search_news(self, query):
        print("The entire date range in %s to %s\r\n" % (self.cnfDict['start_date'], self.cnfDict['end_date']))
        url_format = "http://news.naver.com/main/search/search.nhn?refresh=&so=%s&stPhoto=&stPaper=&stRelease=&detail=0&rcsection=&query=%s&x=24&y=9&sm=all.basic&pd=4&startDate=%s&endDate=%s&page=%i"
        restStart = start_date = self.cnfDict['start_date']
        restEnd = end_date = self.cnfDict['end_date']
        while True:
            while True:
                page = 1
                url = url_format % (self.cnfDict['order'], str(query.replace(" ", "+").encode("cp949")).strip("b").replace("\\x", "%").strip("'"), start_date, end_date, page)
                err_code, soup = self.r.access_page(url, self.cnfDict['retry'])
                if err_code != 1:
                    print("Can't load the page %i" % page)
                    continue
                try:
                    resultCheck = soup.find('div', {'class': 'result_header'}).find('span', {'class': 'result_num'}).text.strip()
                except Exception as e:
                    print(e)
                    print("There's a problem with page %i" % page)
                    continue
                entireCnt = int(re.search(r"\(.+ / (\d+)건\)", resultCheck.replace(",", "")).group(1))
                if entireCnt <= 4000 or start_date == end_date:
                    if start_date == end_date:
                        print("The start date and the end date is now same. entire count: %i\r\n" % entireCnt)
                    print("Range in %s to %s\r\n" % (start_date, end_date))
                    last_page = self.check_page(url)
                    print("There're %i pagelists..." % last_page)
                    print(str(datetime.now()) + "\r\n")
                    for page in list(range(1, last_page + 1)):
                        if page == 1:
                            print("Start page: %i" % page, end="")
                        else:
                            print(", %i" % page, end="")
                        url = url_format % (self.cnfDict['order'], str(query.replace(" ", "+").encode("cp949")).strip("b").replace("\\x", "%").strip("'"), start_date, end_date, page)
                        err_code, soup = self.r.access_page(url, self.cnfDict['retry'])
                        if err_code != 1:
                            print("Can't load the page %i" % page)
                            continue
                        for item in soup.findAll("ul", {"class": "srch_lst"}):
                            a_id = self.get_article(query, item, 0, 0, "")
                    restStart = str((datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)).date())
                    break
                else:
                    print("Reduce date interval...")
                    dateInterval = datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")
                    dateInterval = math.floor(int(dateInterval.days)/2)
                    end_date = str((datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=dateInterval)).date())
            start_date = restStart
            end_date = restEnd

            if start_date > end_date:
                break

    def get_article(self, query, item, sub=0, mother_id=0, mother_url=""):
        content, title, press, a_date, url1, url2, related_group = self.get_basic_info(item, sub)
        # if naver news, url1 is go_naver link. if external news, url1 is external news link.
        rep_url = url1
        if sub == 0 or (sub in (1, 2) and rep_url != mother_url):
        # not sub news OR (sub news AND not same with mother url)
            check = self.mysql.check_inserted_or_not(url1)
            if url2 is not None:        # if there is naver news url
                a_id = self.getNewsAndComment("", url1, check)
                #print("no article... skip....")     #STOP here
                #a_id = 0   # for related news
            else:       # only has outer url on the press
                if check[0] == 1:
                    # already retrieved url
                    a_id = check[1][0]
                    self.mysql.insert_srch_query(query, a_id)
                    if sub in (1, 2):
                        self.mysql.update_rel_article(mother_id, a_id)        # STOP here
                else:
                    # external news AND not yet retrieved
                    err_code, soup = self.r.access_page(url1, self.cnfDict['retry'])
                    if err_code != 1:
                        a_id = self.mysql.insert_url_n_srch_query(query, url1, err_code)              # STOP
                    else:       # there's no error
                        a_cat = ""
                        a_id = self.mysql.insert_url_n_srch_query(query, url1, err_code)
                        isNaver = 0
                        dsc = self.get_dsc(sub, content)
                        from newsCrawler3.externalNews import ExternalNews
                        ext = ExternalNews()
                        err_code, a_body = ext.get_external_news(soup, dsc, url1, self.re_dict)
                        if err_code != 1:
                            self.mysql.update_error_code(a_id, err_code)          # STOP
                        else:
                            r_datetime = datetime.now()
                            var_tuple = (a_id, "naver", press, title.strip('"'), a_body.replace("\n", " ").strip(), a_date, a_cat, isNaver, r_datetime)
                            self.mysql.insert_news(var_tuple)
                if sub in (1, 2):
                    return a_id

            # if there're related news list, go ahead
            if sub == 0 and related_group is not None and related_group.find("span", {"class": "ico_bu"}):
                self.get_related_news(query, related_group, a_id, rep_url)
        return 0


    def get_related_news(self, query, related_group, mother_id, mother_url):
        btn_more = related_group.find("a", {"class": "btn_more"})

        # if there're more related news than 4
        if btn_more is not None:
            more_link = "http://news.naver.com/main/search/search.nhn%s" % btn_more.get('href')
            err_code, soup = self.r.access_page(more_link, self.cnfDict['retry'])
            if err_code != 1:
                pass
            else:
                for item in soup.findAll("ul", {"class": "srch_lst"}):
                    a_id= self.get_article(query, item, 2, mother_id, mother_url)
                    # go to redirect again(this is new list page)
                    if a_id is None:
                        continue
                    self.mysql.update_rel_article(mother_id, a_id)
        # if there're more related news equal or less than 4
        else:
            for item in related_group.findAll("li"):        # each related news items
                a_id = self.get_article(query, item, 1, mother_id, mother_url)
                self.mysql.update_rel_article(mother_id, a_id)


    def getNewsAndComment(self, section, newsLink, check):
        if check[0] == 1:
            # already retrieved url
            a_id = check[1][0]
        else:
            a_id = self.mysql.insert_url(newsLink)
            var_tuple = self.getNewsBody(a_id, section, newsLink)
            if var_tuple[0] in (404, 90, 91, 95):   #404 error, sports, entertain, else
                # error
                self.mysql.update_error_code(a_id, var_tuple[0])
            else:
                self.mysql.insert_news(var_tuple)
                if self.cnfDict['comment'] is True:
                    oid = re.findall(r"oid=(\d+)", newsLink)[0]
                    aid = re.findall(r"aid=(\d+)", newsLink)[0]
                    gno = "news" + oid + "," + aid
                    while True:
                        headers = {
                            'accept-encoding': 'gzip, deflate, sdch',
                            'accept-language': 'ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4',
                            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36',
                            'accept': '*/*',
                            'referer': 'http://news.naver.com/main/ranking/read.nhn?mid=etc&sid1=111&rankingType=memo_week&oid=421&aid=0001843772&date=20160120&type=1&rankingSectionId=100&rankingSeq=1',
                            'cookie': 'NNB=QECI6G5YG4HFM; npic=WXjITWIJ4tuGHKilzfw6Nljt9irLqDTyXcPPQPdLWDv9+/zMx8hTr42F7iTT73h0CA==; BMR=s=1449599642101&r=http%3A%2F%2Fnstore.naver.com%2Fappstore%2Fweb%2Fdetail.nhn%3FproductNo%3D1483986&r2=https%3A%2F%2Fwww.google.co.kr%2F; nid_iplevel=1; nid_inf=-2131057769; page_uid=SqW7SdpyLflsscEivZossssssud-397948; _naver_usersession_=DSLHgTQaLsQL5PF8I4FVLQ==',
                        }
                        timeout = 10.0
                        var_sql, var_tuple = self.getComment(a_id, gno, headers, timeout)
                        break
                    if var_tuple == ():
                        #print("There's no comment. skip...")
                        pass
                    else:
                        #print("Insert to DB")
                        self.mysql.insert_comment(var_sql, var_tuple)
                        time.sleep(2)
        return a_id       #temp


    def getNewsBody(self, a_id, section, newsLink):
        err_code, soup = self.r.access_page(newsLink, self.cnfDict['retry'])
        if err_code == 1:
            try:
                header = soup.find('div', {'class': 'article_header'}).find('div', {'class': 'article_info'})
            except AttributeError:      # naver entertainment news page
                if soup.find("div", {"class": "error_msg 404"}) is not None:
                    return(404,)
                elif newsLink.startswith("http://sports.news.naver.com"):
                    return(90,)
                else:
                    try:
                        redirect_url = soup.find('meta', {'property': 'og:url'})['content']
                        if redirect_url.startswith("http://entertain.naver.com"):
                            return(91,)      # just for now...
                        else:
                            print("Another naver child news site")
                            print(newsLink)
                            return(95,)
                    except Exception as e:
                        print("Another exception page...")
                        print(e)
                        print(newsLink)
                        return(95,)
            press = soup.find('meta', {'property': 'me2:category1'})['content']
            title = header.find('h3', {'id': 'articleTitle'}).text
            a_datetime = header.find('span', {'class': 't11'}).text
            a_datetime = datetime.strptime(a_datetime, '%Y-%m-%d %H:%M')
            a_body = soup.find('div', {'id': 'articleBodyContents'}).text.strip()   # should remove link
            isNaver = 1
            r_datetime = datetime.now()
            return a_id, "naver", press, title.replace("'", "\'"), a_body.replace("'", "\'").replace("\n", " "), \
                   a_datetime, section, isNaver, r_datetime
        else:
            return(404,)


    def getComment(self, a_id, gno, headers, timeout):
        var_sql_list = list()
        var_tuple = tuple()
        page = 1
        rdic = dict()
        rdic['count'] = dict()
        rdic['count']['comment'] = 0
        url = "https://apis.naver.com/commentBox/cbox5/web_naver_list_jsonp.json?ticket=news&templateId=default_politics&_callback=window.__cbox_jindo_callback._8858&lang=ko&country=KR&objectId=" + gno + "&categoryId=&pageSize=20&indexSize=10&groupId=&page=%i&initialize=true&useAltSort=true&replyPageSize=100&moveTo=&sort=favorite&userType="
        while True:
            if page % 10 == 1:
                if page == 1:
                    pass
                else:
                    print(", %i" % page, end="")
            e_num, res = self.r.access_page(url % page, self.cnfDict['retry'], headers=headers)
            if e_num == 1:
                try:
                    t = re.search(r"window\.__cbox_jindo_callback\._8858\((.+)\)", res).group(1)
                    rdic = json.loads(t)['result']
                    anch = True
                except Exception as e:
                    print(e)
                    print("comment parsing error with gno %s..." % gno)
                    anch = False
                    pass
                if anch is True:
                    if 'commentList' not in rdic.keys():
                        pass
                    else:
                        for reply in rdic['commentList']:
                            maskUserId = reply['maskedUserId']
                            encodedUserId = reply['userIdNo']
                            if encodedUserId is None:
                                encodedUserId = ""
                            commentReplyNo = reply['commentNo']
                            sRegDate = reply['regTime']
                            if "오전" in sRegDate:
                                sRegDate = sRegDate.replace("오전", "AM")
                            elif "오후" in sRegDate:
                                sRegDate = sRegDate.replace("오후", "PM")
                            sRegDate = datetime.strptime(sRegDate, "%Y-%m-%dT%H:%M:%S+0900")
                            snsType = ""
                            incomingType = ""
                            badCnt = reply['antipathyCount']
                            goodCnt = reply['sympathyCount']
                            likeCnt = goodCnt-badCnt
                            replyCnt = reply['replyCount']
                            content = reply['contents'].replace("\n\r", " ").replace("\n", " ")
                            if reply['best'] is False:
                                isBest = 0
                            elif reply['best'] is True:
                                isBest = 1
                            c_grade = ""
                            c_pnt = 0
                            c_nextGradePnt = 0
                            var_sql_list.append("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
                            var_tuple += (a_id, commentReplyNo, maskUserId, encodedUserId, sRegDate, content, badCnt, goodCnt, likeCnt, replyCnt, incomingType, snsType, isBest, c_grade, c_pnt, c_nextGradePnt)
                else:
                    pass
            else:
                pass
            try:
                if page < math.ceil(rdic['count']['comment']/20):
                    page += 1
                    time.sleep(0.1)
                else:
                    break
            except KeyError:
                print("KeyError...")
                break
        return(",".join(var_sql_list).strip(","), var_tuple)


    def get_dsc(self, sub, content):
        if sub == 0:
            # get news description part: to find text body easily
            dsc_list = content.find("p", {"class": "dsc"}).get_text(strip=False).strip().split("...")
            dsc_list = [x for x in dsc_list if x != "" and x != " " and x != "."]
            # if there's description, split it using '다.'
            if len(dsc_list) != 0:
                try:
                    dsc = dsc_list[-1].split("다.")[-2].strip() + "다."
                except:
                    dsc = dsc_list[-1].split("다.")[0].strip() + "다."
            # if there's no descripton, then use '다.' instead
            else:
                dsc = "다."
        else:       # sub in (1, 2)
            dsc = "다."
        return dsc


    def get_basic_info(self, item, sub):
        if sub in (0, 2):
            content = item.find("div", {"class": "ct"})
            info = content.find("div", {"class": "info"})
            title = content.find("a", {"class": "tit"}).get_text(strip=True)
            press = info.find("span", {"class": "press"}).get_text(strip=True).replace("\'", "\\'")
            date_text = info.find("span", {"class": "time"}).get_text(strip=True).strip("전")
            date = self.get_news_date(date_text)
            url1 = content.find("a", {"class": "tit"}).get('href')
            go_naver = info.find("a", {"class": "go_naver"})
            if sub == 0:
                related_group = content.find("div", {"class": "related_group"})
            else:#      sub == 2:
                related_group = ""
        else:       #sub == 1
            title = item.find("a").get_text(strip=True).replace("\'", "\\'")
            press = item.find("span", {"class": "press"}).get_text(strip=True).replace("\'", "\\'")
            date_text = item.find("span", {"class": "time"}).get_text(strip=True).strip("전")
            date = self.get_news_date(date_text)
            url1 = item.find("a").get('href')
            go_naver = item.find("a", {"class": "go_naver"})
            content = ""
            related_group = ""
        if go_naver is not None:
            url2 = url1
            url1 = go_naver.get('href')
        else:
            url2 = None
        return (content, title, press, date, url1, url2, related_group)


    def get_news_date(self, date_text):
        if date_text.endswith("분"):
            date = datetime.now() - timedelta(minutes=int(date_text.split("분")[0]))
        elif date_text.endswith("시간"):
            date = datetime.now() - timedelta(hours=int(date_text.split("시간")[0]))
        elif date_text.endswith("일"):
            date = datetime.today() - timedelta(days=int(date_text.split("일")[0]))
        else:
            date = date_text.replace(".", "-") + " 00:00:00"
        return date


    def check_page(self, nextUrl):
        print("start counting the entire pages...")
        print(str(datetime.now()) + "\n")
        current_no = 1
        next_no = 1
        while True:
            if current_no > next_no:
                break
            err_code, soup = self.r.access_page(nextUrl, self.cnfDict['retry'])
            current_no = next_no

            try:
                nextUrl = soup.find("div", {"class": "paging"}).findAll("a")[-1].get('href')
                nextUrl = "http://news.naver.com" + nextUrl
                next_no = int(nextUrl.split("&page=")[1])
            except:
                current_no = 1
                break
        return current_no       # int

    def search_all_section(self, section, sectionDict, sectionDictKo):
        start_date = datetime.strptime(self.cnfDict['start_date'], "%Y-%m-%d").date()
        end_date = datetime.strptime(self.cnfDict['end_date'], "%Y-%m-%d").date()
        while start_date <= end_date:
            print("start date %s" % str(start_date))
            print(datetime.now())
            page = 1
            url = self.url_format % (sectionDict[section], str(start_date), page)
            err_code, soup = self.r.access_page(url, self.cnfDict['retry'])
            if err_code != 1:
                print("Error occurred on date: %s" % str(start_date))
            else:
                comp_id = int(soup.find("a", {"id": "mainNewsComponentId"})['name'])
                url = self.post_url_format % (comp_id, str(start_date), page)
                err_code, html = self.r.access_page(url, self.cnfDict['retry'], headers=None, isSoup=False)
                if err_code != 1:
                    print("Error occurred on date: %s" % str(start_date))
                else:
                    lastPage = json.loads(html)['pagerInfo']['lastPage']
                    while page <= lastPage:
                        url = self.post_url_format % (comp_id, str(start_date), page)
                        err_code, html = self.r.access_page(url, self.cnfDict['retry'], headers=None, isSoup=False)
                        if err_code != 1:
                            print("Error occurred on date %s and page %i" % (str(start_date), page))
                        else:
                            for item in json.loads(html)['itemList']:
                                aid = item['articleId']
                                oid = item['officeId']
                                news_url = self.news_url_format % (sectionDict[section], oid, aid)
                                self.getNews(sectionDictKo[section], news_url)
                        page += 1
            start_date = start_date + timedelta(days=1)

    def getNews(self, section, newsLink):
        check = self.mysql.check_inserted_or_not(newsLink)
        a_id = self.getNewsAndComment(section, newsLink, check)
        '''if check[0] == 1:
            # already retrieved url
            a_id = check[1][0]
        else:
            a_id = self.mysql.insert_url(newsLink)
            var_tuple = self.getNewsBody(a_id, section, newsLink)
            if var_tuple[0] in (404, 90, 91, 95):   #404 error, sports, entertain, else
                # error
                self.mysql.update_error_code(a_id, var_tuple[0])
            else:
                self.mysql.insert_news(var_tuple)'''
