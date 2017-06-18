__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/6/2016'

import requests
import time
from datetime import datetime
import socket
from bs4 import BeautifulSoup


class Req():
    # represent http requests

    def __init__(self, nd):
        self.nd = nd

    def access_page(self, url, maxIter, isSoup=True):
        t = 10.0
        n = 0
        while True:
            n += 1
            if n == maxIter:
                return (10, "Page is not available(manually stop)")
            try:
                res = self.nd._s.get(url, timeout=t).text
                if "<title>400 Bad Request</title>" in res:
                    print("400 Bad request error.... sleep 10 minutes..." + str(datetime.now()))
                    print(url)
                    time.sleep(600) #sleep 10 minutes
                    n = 0
                else:
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
        if isSoup is True:
            return (1, BeautifulSoup(res, "lxml"))
        else:
            return (1, res)     # post comments
