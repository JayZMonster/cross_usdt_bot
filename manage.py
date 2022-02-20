from notifier import Notifier
from parser import Parser
from binance_parser import BinanceParser
from config import *
from time import sleep


def mutate(summaries, bin_prices, straight_cost):
    final = []
    for summar, bin_ in zip(summaries, bin_prices):
        try:
            binance_price = bin_['price']
            def_price = summar['price']
            cross_price = round(float(summar['price']) / float(bin_['price']), 3)
        except:
            cross_price = -1
            binance_price = 0
            def_price = 0
        info = {
            'link': summar['link'],
            'ticker': summar['ticker'],
            'asset_price': float(def_price),
            'binance_price': float(binance_price),
            'cross_price': cross_price,
            'straight_price': float(straight_cost),
            'profit': ((float(straight_cost) / cross_price) - 1) * 100
        }
        final.append(info)
    return final


def get_straight_cost(driver):
    driver.get('https://p2p.binance.com/en?fiat=RUB&payment=TINKOFF')
    sleep(10)
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'lxml')
    vurnku = soup.find('body').find('main', {'class': 'main-content'}).find('div', {'class': 'css-16g55fu'}).find('div',
                                                                                                                  {
                                                                                                                      'class': 'css-1m1f8hn'})
    return vurnku.text


def main(*args):
    notifier = Notifier(token=TG_TOKEN,
                        chat_id=CHAT_ID,
                        )
    parser = Parser(url=URL,
                    asset=ASSET,
                    )

    binance_parser = BinanceParser('', '')
    while True:
        summaries = parser.parse()
        if summaries == 'chill':
            print('Chilling 60 secs')
            sleep(60)
            continue
        straight_cost = get_straight_cost(parser.driver)
        bin_prices = binance_parser.get_all_tickers(summaries)
        final = mutate(summaries, bin_prices, straight_cost)
        notifier.work(final)
        sleep(200)


if __name__ == '__main__':
    main()
