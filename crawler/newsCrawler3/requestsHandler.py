__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/6/2016'

import requests
import time
import socket
from bs4 import BeautifulSoup


class Req():
    # represent http requests

    def __init__(self):
        pass

    def access_page(self, url, maxIter, headers=None, isSoup=True):
        t = 10.0
        n = 0
        if headers is not None:         #comment page call(more retrial)
            maxIter += 3
        while True:
            n += 1
            if n == maxIter:
                return (10, "Page is not available(manually stop)")
            try:
                if headers is None:
                    html = requests.get(url, timeout=t).text
                else:
                    html = requests.get(url, headers=headers, timeout=t).text
                break
            except requests.exceptions.Timeout:
                print("\nTimeout error with url: %s." % url)
                print("Sleep 20 seconds and retry")
                time.sleep(20)
            except requests.exceptions.ConnectionError:
                print("\nMax retrieve error with url: %s." % url)
                print("Sleep 20 seconds and retry")
                time.sleep(20)
            except requests.exceptions.TooManyRedirects:
                #if url.startswith("http://www.christiantoday.co.kr"):
                #    print("\nToo many redirect error on christiantoday, skip...")
                #    return (10, "Page is not available(manually stop)")
                #else:
                print("\nToo many redirect error with url: %s." % url)
                print("Sleep 20 seconds and retry")
                time.sleep(20)
            except requests.exceptions.HTTPError:
                print("\nHttp error with url: %s." % url)
                print("Sleep 5 seconds and retry")
                time.sleep(5)
            except requests.exceptions.RequestException:
                print("\nAmbiguous exception with url: %s." % url)
                print("Sleep 20 seconds and retry")
                time.sleep(20)
            except requests.exceptions.LocationParseError as e:
                print(e)
                return (10, "Page is not available(manually stop)")
            except socket.timeout:
                print("\nSocket Timeout error with url: %s." % url)
                print("Sleep 20 seconds and retry")
                time.sleep(20)
            except ConnectionResetError:
                print("\nConnection reset by peer: %s." % url)
                print("Sleep 20 seconds and retry")
                time.sleep(20)
        if headers is None and isSoup is True:
            return (1, BeautifulSoup(html, "lxml"))     #news article
        else:
            return (1, html)        #naver news comment