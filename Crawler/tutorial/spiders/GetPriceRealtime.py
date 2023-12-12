
import scrapy
import json

class PriceRealtime(scrapy.Spider):
    name = "PriceRealtime"
    # Symbol  mã chứng khoán của các công ti
    # PageSize kích thước tập dữ liệu cần crawl
    start_urls = [
        "https://apipubaws.tcbs.com.vn/stock-insight/v1/intraday/HDB/pv-ins?resolution=1",
    ]
    custom_settings = {
        'FEEDS': {
            'PriceRealtime.jsonl': {
                'format': 'jsonl'
            }
        }

    }

    def parse(self, response):

        
        resp = json.loads(response.body)
        print(resp)
        data = resp.get('data')
        bidAskLog= resp.get("bidAskLog")
        print("data: ", data)
        print("bidAskLog", bidAskLog)
        for datum, bidal in zip(data, bidAskLog):
            yield{
                "date": datum.get("dt"),
                "p":    datum.get("p"),
                "cp":   datum.get("cp"),
                "rcp":  datum.get("rcp"),
                "v":    datum.get("v"),
                "ap1":  bidal.get("ap1"),
                "bp1":  bidal.get("bp1"),
                "av1":  bidal.get("av1"),
                "bv1":  bidal.get("bv1"),
            }

        self.crawler.engine.close_spider(self, 'Closed manually')

