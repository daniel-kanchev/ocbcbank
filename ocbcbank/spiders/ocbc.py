import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from ocbcbank.items import Article


class OcbcSpider(scrapy.Spider):
    name = 'ocbc'
    start_urls = ['https://www.ocbc.com/group/media/release/index.page?category=alltopics']

    def parse(self, response):
        links = response.xpath('//a[@class="link media-filter-media-listing__read-more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h3//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="com__ar-de-tags pt3 pb3 fz-14 d-block d-sm-flex '
                              'align-items-center justify-content-between"]//li/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d %b %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="com__paragraph bp-img wide"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
