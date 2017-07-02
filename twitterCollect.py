import urllib
import urllib.request
import urllib.parse
import bs4
import re
import time
import random
import datetime
import json
import sys

rgxSpace = re.compile('\\s+')

def extractTweets(soup):
    ret = []
    for item in soup.select('.js-stream-item'):
        url = item.select('.time a')[0]['href']
        t = str(datetime.datetime.fromtimestamp(int(item.select('.time a span')[0]['data-time'])))
        cont = rgxSpace.sub(' ',item.select('.js-tweet-text-container p')[0].text)
        reply = item.select('.ProfileTweet-action--reply .ProfileTweet-actionCount')[0]['data-tweet-stat-count']
        retweet = item.select('.ProfileTweet-action--retweet .ProfileTweet-actionCount')[0]['data-tweet-stat-count']
        favorite = item.select('.ProfileTweet-action--favorite .ProfileTweet-actionCount')[0]['data-tweet-stat-count']
        ret.append((url, t, cont, reply, retweet, favorite))
    return ret

def collectTwitter(query, maxN, o, mp = None):
    num = 0
    while not(maxN and num >= maxN):
        for retry in range(5):
            try:
                data = urllib.parse.urlencode(
                    {'f': 'tweets', 'vertical': 'default', 'q': query, 'src': 'typd', 'max_position': mp or ''})
                req = urllib.request.Request('https://twitter.com/search?' + data)
                req.add_header('Referer', 'https://twitter.com/search?' + data)
                req.add_header('User-Agent',
                               'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
                f = urllib.request.urlopen(req)
                cont = f.read().decode('utf-8')
                soup = bs4.BeautifulSoup(cont, "lxml")
                for i in extractTweets(soup):
                    o.write('\t'.join(i) + '\n')
                    num += 1
                    if maxN and num >= maxN: break
                mp = soup.select('.stream-container')[0]['data-max-position']
                print(mp)
                break
            except Exception as e:
                print(e)
                time.sleep(random.randint(30, 90))
        if retry >= 4: exit()
        o.flush()
        time.sleep(random.randint(3, 9))

if __name__ == '__main__':

    if len(sys.argv) <= 1:
        print('USAGE : twitterCollect.py\n')
        print('> python3 twitterCollect.py [query] [maxPosition] [maxN] [outputPath]')
        print('** query: search query')
        print('*** maxN: the number of collected tweets. 0 means unlimited. (default value: 0)')
        print('**** outputPath: the path of output file. (default value: res/"query".txt)')
        exit()
    query = sys.argv[1]
    mp = sys.argv[2] if len(sys.argv) > 2 else None
    maxN = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    output = sys.argv[4] if len(sys.argv) > 4 else 'res/%s.txt' % query
    with open(output, 'w', encoding='utf-8') as o:
        collectTwitter(query, maxN, o, mp)
