from scrapy.utils.reactor import install_reactor
install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')

from tutorial.spiders.GetPriceRealtime import PriceRealtime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import time

from multiprocessing import Process  # Sửa đổi dòng import


def mainRealtime():
    setting = get_project_settings()
    process = CrawlerProcess(setting)
    process.crawl(PriceRealtime)
    process.start()

    # import sys
    # del sys.modules['twisted.internet.reactor']

if __name__ == "__main__":
    while(True):
        p = Process(target=mainRealtime)
        p.start()
        p.join()
        time.sleep(60)