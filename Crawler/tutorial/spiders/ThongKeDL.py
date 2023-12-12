

import scrapy
import json

class ThongKeDLSpider(scrapy.Spider):
    name = "ThongKeDL"
    # Symbol  mã chứng khoán của các công ti
    # PageSize kích thước tập dữ liệu cần crawl
    start_urls = [
        "https://s.cafef.vn/Ajax/PageNew/DataHistory/ThongKeDL.ashx?Symbol=HDB&StartDate=&EndDate=&PageIndex=&PageSize=10000",
    ]
    custom_settings = {
        'FEEDS': {
            'ThongKeDL.jsonl': {
                'format': 'jsonl'
            }
        }

    }

    def parse(self, response):
        resp = json.loads(response.body)
        print(resp)
        data = resp.get('Data').get("Data")
        print("Data: ",data)
        for datum in data:
            yield{
                "date": datum.get("Date"),
                "ThayDoi": datum.get("ThayDoi"),
                "SoLenhMua": datum.get("SoLenhMua"),
                "KLDatMua": datum.get("KLDatMua"),
                "KLTB1LenhMua": datum.get("KLTB1LenhMua"),
                "SoLenhDatBan": datum.get("KLDatBan"),
                "KLTB1LenhBan": datum.get("KLTB1LenhBan"),
                "ChenhLechKL": datum.get("ChenhLechKL")
            }
