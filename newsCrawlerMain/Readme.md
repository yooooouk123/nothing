..contents::
Naver와 KINDS 뉴스 DB에서 뉴스 본문과 메타데이터를 수집하는 모듈입니다.
(Naver news의 경우는 댓글도 수집)

Requirements
--------------------
* This module supports >= python3.4
* Python -- all of the following::
    - pymysql
    - requests
    - beautifulsoup4
* MySQL (latest version is recommended)


Setup
--------------------
* Both cnf files are in your ``newsCrawlerMain/cnf/`` directory
    - database.cnf: setup your mysql login id and password
    - main.cnf: setup your crawling setting(query or date range...)

* ``newsCrawler3`` and ``newsCrawlerMain`` directory should be like below
/home or somewhere/
    └ newsCrawler3/
    └ newsCrawlerMain/
        └ cnf/
            └ database.cnf
            └ main.cnf
            └ news_schema.sql
        └ main.


Quick start
--------------------
* First, open ``main.py`` script and add the location ``newsCrawler3`` is in. You should add the parent directory of ``newsCrawler3``.

    $ sys.path.append('parent directory of <newsCrawler3>')


* You can start crawling using the code below in 'newsCrawlerMain' directory.

    $ python3 main.py


* It will automatically create a database if the target db doesn't exist
