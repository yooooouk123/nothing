# NewsCrawler3

Naver와 KINDS 뉴스 DB에서 뉴스 본문과 메타데이터를 수집하는 모듈입니다.
(Naver news의 경우는 댓글도 수집)

## Requirements
* This module supports >= python3.4
* Python -- all of the following::
    - pymysql
    - requests
    - beautifulsoup4
* MySQL (latest version is recommended)


## Setup
* Both cnf files are in your ``newsCrawlerMain/cnf/`` directory
    - database.cnf: setup your mysql login id and password
    - main.cnf: setup your crawling setting(query or date range...)

* ``newsCrawler3`` and ``newsCrawlerMain`` directory should be like below:

* /home or somewhere/
    - newsCrawler3/
    - newsCrawlerMain/
        - cnf/
            + database.cnf
            + main.cnf
            + news_schema.sql
        - main.py


## Required python package Installation on windows
Open the python3 command prompt, copy and paste code below.

```
import pip3

for pkg in ("bs4", "pymysql", "requests"):
    pip3.main(['install', pkg])
```

Then close the prompt using `exit()` and run `main.py` script.


## Quick start
First, open ``main.py`` script and add the location ``newsCrawler3`` is in. You should add the parent directory of ``newsCrawler3``.

```
    $ sys.path.append('parent directory of <newsCrawler3>')
```

You can start crawling by using the code below in 'newsCrawlerMain' directory
``` sh
    $ python3 main.py
```

`main.py` script looks like below.
```
    import sys
    sys.path.append('<PATH WHERE newsCrawler3 IN>')
    from newsCrawler3 import newsCrawler
    
    nc = newsCrawler.NewsCrawler()
    nc.setCnf("./cnf/main.cnf")
    nc.start_work()
    
    print("\nAll finished")
```

It will automatically create a database if the target db doesn't exist.


