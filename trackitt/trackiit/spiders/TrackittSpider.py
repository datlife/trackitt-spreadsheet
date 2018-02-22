import scrapy
import time
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst


from collections import defaultdict


class SpreadSheetItem(scrapy.Item):
    fields = defaultdict(scrapy.Field)


class TrackittSpider(scrapy.Spider):
    name = 'trackitt'
    allowed_domains = ['trackitt.com']
    start_urls = ['http://www.trackitt.com/usa-immigration-trackers/n400/']

    def parse(self, response):
        # Init item
        spreadsheet = SpreadSheetItem()
        loader = ItemLoader(spreadsheet)

        # extract table
        table = response.xpath("//table[@id='myTable01']")
        # skip the first "watch" column
        table_headers = table.xpath('thead/tr/th//font/text()').extract()[1:]
        table_body = table.xpath('tbody/tr')
        for row in table_body:
            # skip the "watch" column
            for col_idx, cell in enumerate(row.xpath('td')[1:]):
                cell_data = cell.xpath('normalize-space(*//text())').extract_first()
                cell_data = cell_data.encode('utf-8').strip() if len(cell_data) else ''
                loader.add_value(table_headers[col_idx], cell_data)
        yield loader.load_item()

        # Go to the next page
        next_page = response.xpath(".//table[@id='pagtable']//div[@class='paginator']//@href")
        if next_page:
            url_next_page = next_page.extract()[-1]
            request = scrapy.Request(url_next_page, callback=self.parse)
            print("Starting loading page %s" % url_next_page)
            time.sleep(2.0)
            yield request
