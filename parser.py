import requests as r
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.edge.options import Options as E_opt
from selenium import webdriver
from bs4 import BeautifulSoup
from random import randint
from time import sleep


class Parser:

    def __init__(self, url, asset):
        self.url = url
        self.asset = asset
        self.tickers: list = []
        self.driver = None
        self.init_driver()

    def init_driver(self, wind=False):
        if wind:
            self.driver = webdriver.Edge()
        else:
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def parse_page(self, sub=''):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
        }
        self.driver.get(self.url+sub)
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        return soup

    def _add_ticker(self, tr):
        try:
            self._mutate_ticker(tr)
            return 1
        except IndexError:
            self.tickers.pop()
            return 0

    def _mutate_ticker(self, tr):
        if '(' not in tr.text.split(' ')[1]:
            name = tr.text.split(' ')[:2]
            ticker = tr.text.split(' ')[-1][1:-1]
            name = [tick.lower() for tick in name]
            name = '-'.join(name)
            self.tickers.append({
                'name': name,
                'ticker': ticker,
            })
        else:
            name = tr.text.split(' ')[0]
            ticker = tr.text.split(' ')[-1][1:-1]
            self.tickers.append({
                'name': name.lower(),
                'ticker': ticker,
            })

    def _parse_tickers(self):
        page = self.parse_page()
        table_body = page.find('div', {'id': 'curr_tab'}).find('tbody')
        trs = table_body.find_all('tr')
        for tr in trs:
            try:
                tag_class = tr['class']
                if 'hide' in tag_class:
                    continue
                else:
                    var = self._add_ticker(tr)
                    if not var:
                        break
            except KeyError:
                var = self._add_ticker(tr)
                if not var:
                    break
        # Fixing ether-classic to ethereum-classic (service requires)
        for i, ticker in enumerate(self.tickers):
            if ticker['name'] == 'ether-classic':
                self.tickers[i]['name'] = 'ethereum-classic'

    def clear_tickers(self):
        self.tickers = []

    def parse(self):
        # Parsing tickers first of all
        try:
            self._parse_tickers()
            print('Tickers parsed')
        except AttributeError:
            return 'chill'
        summaries = []
        for ticker in self.tickers:
            print(f'Parsing {ticker["name"]}...')
            # Creating a unique url for each pair
            new_url = f'{self.asset}-to-{ticker["name"]}.html'
            page = self.parse_page(new_url)
            exchanges = page.find('div', {'id':'rates_block'})
            best = exchanges.find('tbody').find('tr')
            best_link = best.find('a').get('href')
            price_amount = best.find_all('td', {'class':'bi'})
            best_price = price_amount[0].text.split(' RUB ')[0].split(' ')
            best_price = ''.join(best_price)
            best_amount = price_amount[1].text.split(' ')[0]
            price = float(best_price) / float(best_amount)
            summaries.append({
                'ticker': ticker,
                'link': best_link,
                'price': price,
            })
            sleep(randint(1, 3))
        self.clear_tickers()
        return summaries


# if __name__ == '__main__':
#     parser = Parser('https://www.bestchange.ru/', 'qiwi')
#     msg = parser.parse()
#     print(msg)
