
import scrapy
import json

class GDKhoiNgoaiSpider(scrapy.Spider):
    name = "GDKhoiNgoai"
    # Symbol  mã chứng khoán của các công ti
    # PageSize kích thước tập dữ liệu cần crawl
    start_urls = [
        "https://s.cafef.vn/Ajax/PageNew/DataHistory/GDKhoiNgoai.ashx?Symbol=HDB&StartDate=&EndDate=&PageIndex=&PageSize=10000",
    ]
    custom_settings = {
        'FEEDS': {
            'GDKhoiNgoai.jsonl': {
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
                "KLGDRong": datum.get("KLGDRong"),
                "GTGDRong": datum.get("GTGDRong"),
                "KLMua": datum.get("KLMua"),
                "GtMua": datum.get("GtMua"),
                "KLBan": datum.get("KLBan"),
                "GtBan": datum.get("GtBan"),
                "RoomConLai": datum.get("RoomConLai"),
                "DangSoHuu": datum.get("DangSoHuu")
            }
