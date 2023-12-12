

import scrapy
import json

class GDTuDoanhSpider(scrapy.Spider):
    name = "GDTuDoanh"
    # Symbol  mã chứng khoán của các công ti
    # PageSize kích thước tập dữ liệu cần crawl
    start_urls = [
        "https://s.cafef.vn/Ajax/PageNew/DataHistory/GDTuDoanh.ashx?Symbol=HDB&StartDate=&EndDate=&PageIndex=&PageSize=10000",
    ]
    custom_settings = {
        'FEEDS': {
            'GDTuDoanh.jsonl': {
                'format': 'jsonl'
            }
        }

    }

    def parse(self, response):
        resp = json.loads(response.body)
        print(resp)
        data = resp.get('Data').get("Data").get("ListDataTudoanh")
        print("Data: ",data)
        for datum in data:
            yield{
                "date": datum.get("Date"),
                "KLcpMua": datum.get("KLcpMua"),
                "KLcpBan": datum.get("KLcpBan"),
                "GtMua": datum.get("GtMua"),
                "GtBan": datum.get("GtBan"),
            }
