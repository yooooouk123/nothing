__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '5/31/2016'


import os
import re
import binascii
import mimetypes
import shutil
import datetime
import requests
import rsa
from bs4 import BeautifulSoup


def encrypt(key_str, uid, upw):
    def naver_style_join(l):
        return ''.join([chr(len(s)) + str(s).strip("b'") for s in l]).encode()

    sessionkey, keyname, e_str, n_str = key_str.split(b',')   # modified
    e, n = int(e_str, 16), int(n_str, 16)

    message = naver_style_join([sessionkey, uid, upw])

    pubkey = rsa.PublicKey(e, n)
    encrypted = rsa.encrypt(message, pubkey)

    return keyname, binascii.hexlify(encrypted)


def encrypt_account(uid, upw):
    key_str = requests.get('http://static.nid.naver.com/enclogin/keys.nhn').content
    return encrypt(key_str, uid, upw)


def naver_session(nid, npw):
    encnm, encpw = encrypt_account(nid, npw)
    encnm = encnm.decode()
    encpw = encpw.decode()

    s = requests.Session()
    resp = s.post('https://nid.naver.com/nidlogin.login', data={
        'svctype': '0',
        'enctp': '1',
        'encnm': encnm,
        'enc_url': 'http0X0.0000000000001P-10220.0000000.000000www.naver.com',
        'url': 'www.naver.com',
        'smart_level': '1',
        'encpw': encpw,
    })
    rc = resp.content.decode()
    #print(rc)
    finalize_url = re.search(r'location\.replace\("([^"]+)"\)', rc).group(1)
    s.get(finalize_url)

    return s


class NdriveError(Exception):
    class Codes(object):
        NotExistPath = 11

    def __init__(self, code, message):
        self.code = code
        self.message = message


class Ndrive(object):
    class Types(object):
        DIR = 1

    class TypeNames(object):
        DIR = 'collection'
        FILE = 'property'

    def __init__(self, userid, npw):
        self._userid = userid
        self._useridx = None
        self._s = naver_session(userid, npw)

    @staticmethod
    def _check_error(data):
        if data['resultcode'] != 0:
            raise NdriveError(data['resultcode'], data['message'])

    def check_status(self):
        resp = self._s.get('http://ndrive2.naver.com/GetRegisterUserInfo.ndrive', params={
            'userid': self._userid,
            'svctype': 'Android NDrive App ver',
            'auto': 0
        })
        data = resp.json()
        self._check_error(data)

        self._useridx = data['resultvalue']['useridx']

        return data['resultvalue']

    def list_dirs(self, target_path):
        if not self._useridx:
            self.check_status()

        resp = self._s.post('http://ndrive2.naver.com/GetList.ndrive', data={
            'orgresource': target_path,
            'type': self.Types.DIR,
            'dept': 0,
            'sort': 'name',
            'order': 'asc',
            'startnum': 0,
            'pagingrow': 1000,
            'dummy': 56184,
            'userid': self._userid,
            'useridx': self._useridx,
        })
        data = resp.json()
        self._check_error(data)

        return data['resultvalue']

    def make_dir(self, target_path):
        if not self._useridx:
            self.check_status()

        resp = self._s.post('http://ndrive2.naver.com/MakeDirectory.ndrive', data={
            'dstresource': target_path,
            'userid': self._userid,
            'useridx': self._useridx,
            'dummy': 40841,
        })
        data = resp.json()
        self._check_error(data)

        return True

    def get_disk_space(self):
        if not self._useridx:
            self.check_status()

        resp = self._s.post('http://ndrive2.naver.com/GetDiskSpace.ndrive', data={
            'userid': self._userid,
            'useridx': self._useridx,
        })
        data = resp.json()
        self._check_error(data)

        return data['resultvalue']['unusedspace']

    def check_upload(self, target_path, fp, overwrite=True):
        if not self._useridx:
            self.check_status()

        file_stat = os.fstat(fp.fileno())
        print(datetime.datetime.fromtimestamp(file_stat.st_mtime))

        resp = self._s.post('http://ndrive2.naver.com/CheckUpload.ndrive', data={
            'userid': self._userid,
            'useridx': self._useridx,
            'overwrite':  'T' if overwrite else 'F',
            'uploadsize': file_stat.st_size,
            'getlastmodified': datetime.datetime.fromtimestamp(file_stat.st_mtime),
            'dstresource': target_path,
        })
        data = resp.json()
        self._check_error(data)

        print(data)

        return True

    def get_fileinfo(self, target_path):
        if not self._useridx:
            self.check_status()

        resp = self._s.post('http://ndrive2.naver.com/GetProperty.ndrive', data={
            'orgresource': target_path,
            'userid': self._userid,
            'useridx': self._useridx,
            'dummy': 56184,
        })
        data = resp.json()
        self._check_error(data)

        return data['resultvalue']

    def exists(self, target_path):
        try:
            self.get_fileinfo(target_path)
            return True
        except NdriveError as e:
            if e.code != NdriveError.Codes.NotExistPath:
                raise e
            return False

    def upload(self, target_path, fp, overwrite=True):
        if not self._useridx:
            self.check_status()

        # self.get_disk_space()
        # self.check_upload(target_path, fp, overwrite)

        file_stat = os.fstat(fp.fileno())
        mime = mimetypes.guess_type(target_path)[0]

        resp = self._s.put('http://ndrive2.naver.com' + target_path, data=fp, headers={
            'userid': self._userid,
            'useridx': self._useridx,
            'MODIFYDATE': datetime.datetime.fromtimestamp(file_stat.st_mtime),
            'Content-Type': mime or 'application/octet-binary',
            'charset': 'UTF-8',
            'Origin': 'http://ndrive2.naver.com',
            'OVERWRITE': 'T' if overwrite else 'F',
            'X-Requested-With': 'XMLHttpRequest',
            'NDriveSvcType': 'NHN/DRAGDROP Ver',
            "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        })

        data = resp.json()
        self._check_error(data)

        return True

    def download(self, target_path, download_path):
        if not self._useridx:
            self.check_status()

        resp = self._s.get('http://ndrive2.naver.com' + target_path, params={
            'attachment': 2,
            'userid': self._userid,
            'useridx': self._useridx,
            'NDriveSvcType': 'NHN/ND-WEB Ver',
        }, stream=True)

        resp.raw.decode_content = True
        shutil.copyfileobj(resp.raw, open(download_path, 'wb+'))



if __name__ == "__main__":
    nd = Ndrive("cocainforest", "hqam300!*")
    url = "http://m.cafe.naver.com/ArticleList.nhn?search.clubid=10050813&search.menuid=3618&search.boardtype=L"
    r = nd._s.post(url)

    soup = BeautifulSoup(r.text, "lxml")
    #print(soup)
    for page in soup.find("div", {"id": "articleListArea"}).find_all("a"):
        print(page['href'])
    print("finish")

