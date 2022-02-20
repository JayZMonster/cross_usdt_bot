import pprint

from binance import Client
import requests as r
from bs4 import BeautifulSoup
from binance.exceptions import *
from typing import List


class BinanceParser:

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client: Client
        self._init_client()

    def _init_client(self):
        self.client = Client(self.api_key, self.api_secret)

    @staticmethod
    def get_usd_p2p():
        content = r.get('https://p2p.binance.com/en?fiat=RUB&payment=TINKOFF')
        soup = BeautifulSoup(content.text, 'lxml')
        # find('div').find_all('div')[1].find('main').find('div', {'class': 'css-16g55fu'}).find('div').find_all('div')
        vurnku = soup.find('body').find('main', {'class': 'main-content'}).find('div', {'class': 'css-16g55fu'}).find('div', {'class': 'css-1m1f8hn'})

        pprint.pprint(soup)
        price = vurnku.find('div').find('div').find_all('div')[1].text
        print(price)
        return price

    def get_cost(self, ticker='USDTRUB'):
        try:
            ticker = self.client.get_ticker(symbol=ticker)
            return ticker['lastPrice']
        except BinanceAPIException as e:
            print(e)

    def get_all_tickers(self, _tickers: List[dict]):
        all_prices = []
        for ticker in _tickers:
            semi_ticker = ticker['ticker']['ticker']
            full_ticker = semi_ticker + 'USDT'
            price = self.get_cost(full_ticker)
            info = {'ticker': semi_ticker, 'price': price}
            all_prices.append(info)
        return all_prices


if __name__ == '__main__':
    bp = BinanceParser('', '')
    tickers = [{
        'ticker': {
            'ticker': 'BCH'
        }
    }]
    print(bp.get_usd_p2p())
