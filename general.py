from notifier import Notifier
from parser import Parser, webdriver
from config import *
from time import sleep


def mutate(summaries, straight_cost):
    final = []
    for summar in summaries:
        def_price = summar['price']
        info = {
            'link': summar['link'],
            'ticker': summar['ticker'],
            'asset_price': float(def_price),
            'straight_price': float(straight_cost),
            'profit': ((float(straight_cost) / float(def_price)) - 1) * 100
        }
        final.append(info)
    return final


def get_straight_cost(driver: webdriver.Chrome):
    found = False
    while not found:
        try:
            print('getting p2p price\n')
            driver.get('https://p2p.binance.com/ru/trade/buy/USDT?fiat=RUB&payment=TINKOFF')
            sleep(10)
            try:
                driver.find_element_by_xpath("/html/body/div[8]/div/div[2]/button[1]").click()
            except:
                pass
            try:
                selects = driver.find_elements_by_xpath('//*[@id="onetrust-consent-sdk"]/div[1]')
                for select in selects:
                    driver.execute_script(
                        "arguments[0].setAttribute('class', 'onetrust-pc-dark-filter ot-hide ot-fade-in')", select)
            except:
                pass
            try:
                driver.find_element_by_css_selector('body > div.css-vp41bv > div > svg').click()
            except:
                pass
            element = driver.find_element_by_id('onetrust-style')
            driver.execute_script("""
                var element = arguments[0];
                element.parentNode.removeChild(element);
                """, element)
            driver.find_element_by_xpath("/html/body/div[1]/div[2]/main/div[4]/div/div[1]/div[3]/div[2]/div[1]").click()
            driver.find_element_by_xpath('//*[@id="Тинькофф"]/div/div[2]').click()
            sleep(5)
            vurnku = driver.find_element_by_xpath(
                "/html/body/div[1]/div[2]/main/div[5]/div/div[2]/div[1]/div[1]/div[2]/div/div/div[1]").text

            if vurnku is not None:
                found = True
            else:
                raise Exception
        except:
            sleep(5)
            continue
    return vurnku


def main():
    print(f'Started USDT bot')
    notifier = Notifier(token=TG_TOKEN,
                        chat_id=CHAT_ID,
                        )
    parser = Parser(url=URL,
                    asset=ASSET,
                    tickers=ticker_list,
                    )
    while True:
        summaries = parser.parse()
        if summaries == 'chill':
            print('Chilling 60 secs')
            sleep(60)
            continue
        straight_cost = get_straight_cost(parser.driver)
        print(straight_cost)
        final = mutate(summaries, straight_cost)
        notifier.work(final)
        sleep(200)


if __name__ == '__main__':
    main()
