__author__ = 'Lynn'
__email__ = 'lynnn.hong@gmail.com'
__date__ = '4/4/2016'
__version__ = '3.0.0'
'''
tested on python 3.0
'''
import sys
sys.path.append('/home/tsmm/crawler/')
from newsCrawler3 import newsCrawler

nc = newsCrawler.NewsCrawler()
nc.setCnf("./cnf/main.cnf")
nc.start_work()

print("\nAll finished")
