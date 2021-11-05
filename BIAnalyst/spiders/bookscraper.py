import json
import time

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
        # options.headless = True
        options.add_argument("--window-size=1920,1200")
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        driver.get('https://www.goodreads.com/book/popular_by_date/2021')
        # Wait max 10 sec for whole page load
        time.sleep(10)
        while True:
            try:
                # Show more books button click with explicit wait
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Show more books')]"))).click()
            except Exception as e:
                break
        time.sleep(5)
        source = driver.page_source
        response = Selector(text=source)
        print("The")
        driver.quit()
        divs = response.xpath('//div[@class="RankedBookList"]')
        href_list = divs.xpath('.//div[@class="BookListItem__cover"]/a/@href').extract()
        # href_one = ['https://www.goodreads.com/book/show/54189398-the-spanish-love-deception']
        for url in href_list:
            yield scrapy.Request(url=url, callback=self.parse_books_detail)

    def parse_books_detail(self, response):
        """
        For parsing single book detail
        :param response:
        :return:
        """

        # ''''''''''''''''' Different ways to get book title/name'''''''''''''''#
        book_name = response.selector.xpath('//h1/text()').get().strip()
        book_title = response.selector.xpath('//title/text()').get()  # Another way
        buk_name = response.xpath('//meta[@property="books:isbn"]/@content').extract()
        # ''''''''''''''''''''Pages count''''''''''''''''''#
        pages_count = int(response.xpath('//meta[@property="books:page_count"]/@content').extract()[0])
        # ''''''''''''''''''''Published date''''''''''''''''''#
        published_date = response.xpath('//div[@id="details"]/div[@class="row"]/text()').extract()[1]

        # ''''''''''''''''''''ISBN''''''''''''''''''#
        ISBN = ''.join(response.xpath('//meta[@property="books:isbn"]/@content').extract())
        # ''''''''''''''''''''Genre List''''''''''''''''''#
        divs = response.xpath('//div[@class="bigBoxContent containerWithHeaderContent"]')[6]
        genre_list = []
        for href in divs.xpath('.//a[@class="actionLinkLite bookPageGenreLink"]/text()'):
            genre_list.append(href.extract())
        # ''''''''''''''''''''Rating Value''''''''''''''''''#
        rating_value = float(
            ''.join(map(str, response.xpath('//span[@itemprop="ratingValue"]/text()').extract())).strip())
        # ''''''''''''''''''''Rating Score''''''''''''''''''#
        rating_score = int(
            ''.join(map(str, response.xpath('//meta[@itemprop="ratingCount"]/@content').extract())).strip())
        author = ''.join(map(str, response.xpath('//span[@itemprop="name"]/text()').extract()))
        # ''''''''''''''''''''Description''''''''''''''''''#
        description = ''.join(map(str, response.xpath('//div[@id="description"]/span/text()').extract()))
        # ''''''''''''''''''''URL''''''''''''''''''#
        url = str(response.request.url)
        single_book_detail = dict(ISBN=ISBN, book_name=book_name, url=url, author=author, description=description,
                                  rating_value=rating_value, rating_score=rating_score, genres=genre_list)
        # Save books details
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

        output_file = open('Data_1.json', 'w', encoding='utf-8', )
        json_object = json.dumps(data, indent=4)
        output_file.write(json_object)
