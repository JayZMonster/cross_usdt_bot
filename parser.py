import requests as r
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver
from bs4 import BeautifulSoup
from random import randint
from time import sleep


class Parser:

    def __init__(self, url, asset, tickers):
        self.url = url
        self.asset = asset
        self.tickers: list = tickers
        self.driver = None
        try:
            self.init_driver()
        except:
            sleep(5)
            self.init_driver()

    #def init_driver(self):
     #   chrome_options = Options()
      #  chrome_options.add_argument('--no-sandbox')
       # chrome_options.add_argument('--headless')
        #self.driver = webdriver.Chrome(executable_path='chromedriver', chrome_options=chrome_options)

    def init_driver(self, wind=False):
        if wind:
            self.driver = webdriver.Edge()
        else:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def parse_page(self, sub=''):
        print(self.driver.name)
        try:
            self.driver.get('view-source:'+self.url+sub)
        except:
            self.driver.get(self.url+sub)
        content = self.driver.find_element_by_tag_name('body').text
        soup = BeautifulSoup(content, 'lxml')
        return soup

    # def _add_ticker(self, tr):
    #     try:
    #         self._mutate_ticker(tr)
    #         return 1
    #     except IndexError:
    #         self.tickers.pop()
    #         return 0
    #
    # def _mutate_ticker(self, tr):
    #     if '(' not in tr.text.split(' ')[1]:
    #         name = tr.text.split(' ')[:2]
    #         ticker = tr.text.split(' ')[-1][1:-1]
    #         name = [tick.lower() for tick in name]
    #         name = '-'.join(name)
    #         self.tickers.append({
    #             'name': name,
    #             'ticker': ticker,
    #         })
    #     else:
    #         name = tr.text.split(' ')[0]
    #         ticker = tr.text.split(' ')[-1][1:-1]
    #         self.tickers.append({
    #             'name': name.lower(),
    #             'ticker': ticker,
    #         })
    #
    # def _parse_tickers(self):
    #     page = self.parse_page()
    #     table_body = page.find('div', {'id': 'curr_tab'}).find('tbody')
    #     trs = table_body.find_all('tr')
    #     for tr in trs:
    #         try:
    #             tag_class = tr['class']
    #             if 'hide' in tag_class:
    #                 continue
    #             else:
    #                 var = self._add_ticker(tr)
    #                 if not var:
    #                     break
    #         except KeyError:
    #             var = self._add_ticker(tr)
    #             if not var:
    #                 break
    #     # Fixing ether-classic to ethereum-classic (service requires)
    #     for i, ticker in enumerate(self.tickers):
    #         if ticker['name'] == 'ether-classic':
    #             self.tickers[i]['name'] = 'ethereum-classic'
    #
    # def clear_tickers(self):
    #     self.tickers = []

    def parse(self):
        # Parsing tickers first of all
        summaries = []
        for ticker in self.tickers:
            if ticker["name"] == 'bittorrent':
                break
            print(f'Parsing {ticker["name"]}...')
            # Creating a unique url for each pair
            new_url = f'{self.asset}-to-{ticker["name"]}.html'
            try:
                page = self.parse_page(new_url)
                exchanges = page.find('div', {'id':'rates_block'})
                best = exchanges.find('tbody').find('tr')
                best_link = best.find('a').get('href')
                price_amount = best.find_all('td', {'class':'bi'})
                best_price = price_amount[0].text.split(' RUB ')[0].split(' ')
                best_price = ''.join(best_price)
                best_amount = price_amount[1].text.split(' ')[0]
                price = float(best_price) / float(best_amount)
            except:
                print('Skipped!')
                continue
            summaries.append({
                'ticker': ticker,
                'link': best_link,
                'price': price,
            })
            sleep(randint(1, 3))
        return summaries


# if __name__ == '__main__':
#     parser = Parser('https://www.bestchange.ru/', 'qiwi')
#     msg = parser.parse()
#     print(msg)
