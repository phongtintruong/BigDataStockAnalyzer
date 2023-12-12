

import scrapy
import json

class PriceHistorySpider(scrapy.Spider):
    name = "PriceHistory"
    # Symbol  mã chứng khoán của các công ti
    # PageSize kích thước tập dữ liệu cần crawl
    start_urls = [
        "https://s.cafef.vn/Ajax/PageNew/DataHistory/PriceHistory.ashx?Symbol=HDB&StartDate=&EndDate=&PageIndex=&PageSize=10000",
    ]
    custom_settings = {
        'FEEDS': {
            'PriceHistory.jsonl': {
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
                "date": datum.get("Ngay"),
                "ThayDoi": datum.get("ThayDoi"),
                "GiaDieuChinh": datum.get("GiaDieuChinh"),
                "GiaDongCua": datum.get("GiaDongCua"),
                "KhoiLuongKhopLenh": datum.get("KhoiLuongKhopLenh"),
                "GiaTriKhopLenh": datum.get("GiaTriKhopLenh"),
                "KLThoaThuan": datum.get("KLThoaThuan"),
                "GtThoaThuan": datum.get("GtThoaThuan"),
                "GiaMoCua": datum.get("GiaMoCua"),
                "GiaCaoNhat": datum.get("GiaCaoNhat"),
                "GiaThapNhat": datum.get("GiaThapNhat")
            }
