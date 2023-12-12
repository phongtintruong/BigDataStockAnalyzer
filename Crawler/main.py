from tutorial.spiders.ThongKeDL import ThongKeDLSpider
from tutorial.spiders.GDTuDoanh import GDTuDoanhSpider
from tutorial.spiders.GDKhoiNgoai import GDKhoiNgoaiSpider
from tutorial.spiders.PriceHistory import PriceHistorySpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
def main():
    setting = get_project_settings()
    process = CrawlerProcess(setting)
    process.crawl(ThongKeDLSpider)
    process.crawl(GDTuDoanhSpider)
    process.crawl(GDKhoiNgoaiSpider)
    process.crawl(PriceHistorySpider)
    process.start()



if __name__ == "__main__":
    main()