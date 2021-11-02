import json
import time
import requests
import pandas as pd
import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

details = []
href_list = []


class BookScraper(scrapy.Spider):
    name = "bookscraper"
    allowed_domains = ['goodreads.com']

    def start_requests(self):
        """
        Initial point of spider for scraping
        :return:
        """
        # -------------  (todo For scraping the whole website or all books---------------#

        # base_url = 'https://www.goodreads.com/book/show/'
        # whole_url_list = ['%s%d' % (base_url, x) for x in range(59511272)]

        # ------------- (todo For scraping the whole website or all books---------------#

        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        # pdb.set_trace()
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        # driver.get("https://www.python.org")
        driver.get('https://www.goodreads.com/book/popular_by_date/2021')
        time.sleep(10)
        while True:
            try:
                # loadMoreButton = driver.find_element("//button[contains(@aria-label,'Load more')]")
                # driver.get('https://www.goodreads.com/book/popular_by_date/2021')
                # loadMoreButton = driver.find_element("//button[@class='Button Button--secondary Button--small']/following-sibling::span[text()='Show more books']")
                # loadMoreButton = driver.find_element("//button[@type='button' and span='Show more books']")

                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Show more books')]"))).click()

            except Exception as e:
                break
        time.sleep(5)
        # driver.page_source
        source = driver.page_source
        # time.sleep(10)

        response = Selector(text=source)
        print("The")
        driver.quit()
        # self.parse_urls(response=response)
        # start_urls = ['https://www.goodreads.com/book/popular_by_date/2021']
        # for url in start_urls:
        #     yield scrapy.Request(url=url, callback=self.parse_urls)
        divs = response.xpath('//div[@class="RankedBookList"]')
        href_list = divs.xpath('.//div[@class="BookListItem__cover"]/a/@href').extract()
        for url in href_list:
            yield scrapy.Request(url=url, callback=self.parse_books_detail)

    def parse_urls(self, response):
        """
        Parsing function for getting urls_list
        :param response:
        :return:
        """
        print("TEst")

        divs = response.xpath('//div[@class="RankedBookList"]')

        href_list = divs.xpath('.//div[@class="BookListItem__cover"]/a/@href').extract()
        # for href in divs.xpath('.//div[@class="BookListItem__cover"]/a/@href').extract():
        #     href_list.append(href)

        for url in href_list:
            yield scrapy.Request(url=url, callback=self.parse_books_detail)
        # a = 'https://kxbwmqov6jgg3daaamb744ycu4.appsync-api.us-east-1.amazonaws.com/graphql'

        # divs = response.xpath('//div[@class="RankedBookList"]')
        # # main_container = response.xpath('//div[@class="PopularByDatePage__listContainer"]')
        # # for item in main_container:
        # #     pdb.set_trace()
        # #     print(item)
        # # pdb.set_trace()
        # for divqw in divs:
        #     #pdb.set_trace()
        #     urls = divqw.xpath('//h3[@class="Text Text__title3 Text__umber"]/strong/a')
        #     for url in urls.xpath('.//'):
        #         pdb.set_trace()
        #         print(url)
        #     divqw.xpath('//h3[@class="Text Text__title3 Text__umber"]/strong/a')
        #
        #
        # divs = response.xpath('//h3[@class="Text Text__title3 Text__umber"]').extract()
        # for div in divs:
        #     pdb.set_trace()
        #     print(div)
        #     response = scrapy.Selector(text="""
        #     {div}""")
        #     print(response)
        #     pdb.set_trace()

    def parse_books_detail(self, response):
        """
        For parsing single book detail
        :param response:
        :return:
        """
        url = str(response.request.url)
        #r = requests.
        book_name = response.selector.xpath('//h1/text()').get().strip()
        # response.xpath('//div[@itemprop="FeaturedDetails"]/text()').extract()

        rating_value = float(
            ''.join(map(str, response.xpath('//span[@itemprop="ratingValue"]/text()').extract())).strip())
        # response.css('[itemprop="ratingValue"]::text').extract()
        rating_score = float(
            ''.join(map(str, response.xpath('//meta[@itemprop="ratingCount"]/@content').extract())).strip())
        author = ''.join(map(str, response.xpath('//span[@itemprop="name"]/text()').extract()))
        description = ''.join(map(str, response.xpath('//div[@id="description"]/span/text()').extract()))
        url = str(response.request.url)
        ratings = dict(ratings_score=rating_value, rating_count=rating_score)
        print("--------------------" + book_name + "-------------------------")
        # pdb.set_trace()
        single_book_detail = dict(book_name=book_name, url=url, author=author, ratings=ratings, description=description)

        self.save(single_book_detail)

    def save(self, single_book_detail):
        """
        For writing the json data into file
        :param single_book_detail:
        :return:
        """
        data = json.load(open('Data.json'))
        # convert data to list if not
        if type(data) is dict:
            data = [data]
        # append new item to data lit
        data.append(single_book_detail)

        output_file = open('Data.json', 'w', encoding='utf-8', )
        json_object = json.dumps(data, indent=4)
        output_file.write(json_object)

    def read_data(self):

        df = pd.read_json('Data.json')

        print(df.to_string())
