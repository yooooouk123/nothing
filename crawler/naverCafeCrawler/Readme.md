# naverCafeCrawler

Naver에서 naver cafe 포스트, 댓글과 메타데이터를 수집하는 모듈입니다.

## Requirements
* This module supports >= python3.4
* Python -- all of the following::
    - pymysql
    - requests
    - beautifulsoup4
    - rsa
* MySQL (latest version is recommended)


## Setup
* Both cnf files are in your ``naverCafeCrawlerMain/cnf/`` directory
    - database.cnf: setup your mysql login id and password
    - main.cnf: setup your crawling setting(query or date range...)

* ``naverCafeCrawler`` and ``naverCafeCrawlerMain`` directory should be like below:

⋅⋅⋅/home or somewhere/
    naverCafeCrawler/
⋅⋅⋅ naverCafeCrawlerMain/
        + └ cnf/
            + └ database.cnf
            + └ main.cnf
            + └ naver_cafe_schema.sql
        + └ main.

## Required python package Installation on windows
Open the python3 command prompt, copy and paste code below.
```python3
import pip3

for pkg in ("bs4", "pymysql", "requests", "rsa"):
    pip3.main(['install', pkg])
```
Then close the prompt using `exit()` and run `main.py` script.

## Quick start
First, open ``main.py`` script and add the location ``naverCafeCrawler`` is in. You should add the parent directory of ``naverCafeCrawler``.


``` python3
    $ sys.path.append('parent directory of <naverCafeCrawler>')
```

You can start crawling by using the code below in 'naverCafeCrawlerMain' directory
``` sh
    $ python3 main.py
```

It will automatically create a database if the target db doesn't exist


