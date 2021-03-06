from selenium import webdriver
import math
import time
from datetime import datetime, date
import csv


browser = webdriver.Chrome('./chromedriver')
browser.maximize_window()

browser.get('https://bscscan.com/tokentxns')

pages = 10

records = {}

now = datetime.now()
current_time = now.strftime(" | %H:%M")

csvFileName = str(date.today()) + str(current_time) + '.csv'
file = open(csvFileName, "w")


for page in range(1, pages + 1):

    rows = len(browser.find_elements_by_xpath(
        '//*[@id="content"]/div[2]/div/div/div[2]/table/tbody/tr'))

    coins = {}
    bscscanLinkCount = 1

    for r in range(1, rows + 1):
        coinXPath = '//*[@id="content"]/div[2]/div/div/div[2]/table/tbody/tr[' + \
            str(r) + ']/td[9]/a'

        # If not new coin image (grey), then skip it
        imageSource = browser.find_element_by_xpath(
            coinXPath + '/img').get_attribute('src')
        if imageSource != 'https://bscscan.com/images/main/empty-token.png':
            continue

        # Getting coin name and ticket symbol
        coinElement = browser.find_element_by_xpath(coinXPath)
        ticker = coinElement.text[coinElement.text.find(
            "(") + 1:coinElement.text.find(")")]
        name = coinElement.text

        if 'LPs' in name or 'Pancake LPs' in name:
            continue

        # Getting link for coins and opening it
        bscLink = browser.find_element_by_xpath(
            coinXPath).get_attribute('href')
        # Getting contract
        contract = bscLink.replace('https://bscscan.com/token/', '')

        # Appending everything into a dictionary
        coinInfo = [name, ticker, bscLink]
        coins[contract] = coinInfo

    # Opening tabs
    for contract in coins:
        browser.execute_script(
            'window.open("' + coins[contract].pop() + '","_blank");')
        bscscanLinkCount += 1

    # Transfers and holders information
    for i in range(1, bscscanLinkCount):
        browser.switch_to.window(browser.window_handles[-1])

        print("Currently on: " + browser.title)

        supply = browser.find_element_by_xpath('//*[@id="ContentPlaceHolder1_divSummary"]/div[1]/div[1]/div/div[2]/div[2]/div[2]/span[1]').text
        
        if supply == '0':
            browser.close()
            continue

        numOfHolders = browser.find_element_by_xpath(
            '//*[@id="ContentPlaceHolder1_tr_tokenHolders"]/div/div[2]/div/div').text

        contract = browser.current_url.replace(
            'https://bscscan.com/token/', '')

        # Get the tokens list iframe and switch to it
        iframe = browser.find_element_by_xpath('//*[@id="tokentxnsiframe"]')
        browser.switch_to.frame(iframe)

        # Now you can go through each transfer directly
        # top10Transfers = 0

        transfersInLastMin = 0
        transferLength = len(browser.find_elements_by_xpath(
            '//*[@id="maindiv"]/div[2]/table/tbody/tr'))

        for transferNum in range(1, transferLength):
            transfer = browser.find_element_by_xpath(
                f'//*[@id="maindiv"]/div[2]/table/tbody/tr[{transferNum}]/td[3]/span').text
            if 'sec' in transfer:
                transfersInLastMin += 1

        # Getting the first transaction from the last page of all transactions
        try:
            lastTransactionPage = browser.find_element_by_xpath(
                '//*[@id="maindiv"]/div[1]/nav/ul/li[5]/a')
            lastTransactionPage.click()
        except:
            print('first page is also the last page')

        browser.switch_to.default_content()
        browser.switch_to.frame(iframe)

        # Getting the length of transactions on the last page

        # lastTransactionPageRowLength = len(browser.find_elements_by_xpath(
        #     '//*[@id="maindiv"]/div[2]/table/tbody/tr'))
        # try:
        #     lastTransaction = browser.find_element_by_xpath(
        #         f'//*[@id="maindiv"]/div[2]/table/tbody/tr[1]/td[{lastTransactionPageRowLength}]/span').text
        # except:
        #     lastTransaction = 'Not Found'

        # Getting holder information
        browser.switch_to.default_content()

        holdersTab = browser.find_element_by_xpath(
            '//*[@id="ContentPlaceHolder1_tabHolders"]')
        holdersTab.click()

        iframe = browser.find_element_by_xpath('//*[@id="tokeholdersiframe"]')
        browser.switch_to.frame(iframe)

        top10Holders = 0.0
        holderLength = len(browser.find_elements_by_xpath(
            '//*[@id="maintable"]/div[3]/table/tbody/tr'))

        numHolders = 0
        ten = 10
        if holderLength > 10:
            for i in range(1,  ten + 1):

                try:
                    browser.find_element_by_xpath(
                        f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/i')

                except:
                    holderPercentage = browser.find_element_by_xpath(
                        f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[4]')
                    holderPercentage = holderPercentage.text.replace('%', '')
                    try:
                        top10Holders += float(holderPercentage)
                        numHolders += 1
                    except:
                        top10Holders += 0
                        print("unable to convert holder percentage to float")
                i -= 1

        else:
            for i in range(1, holderLength + 1):

                try:
                    browser.find_element_by_xpath(
                        f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/i')

                except:
                    holderPercentage = browser.find_element_by_xpath(
                        f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[4]')
                    holderPercentage = holderPercentage.text.replace('%', '')
                    try:
                        top10Holders += float(holderPercentage)
                        numHolders += 1
                    except:
                        top10Holders += 0
                        print("unable to convert holder percentage to float")
                i -= 1

        try:
            top10Holders /= numHolders
            top10Holders = round(top10Holders, 3)
        except:
            print('cant divide by 0')
            top10Holders = 0

        top10Holders = str(top10Holders) + "%"

        # Getting top holder
        topHolderPercentage = ''
        for i in range(1, holderLength + 1):
            try:
                browser.find_element_by_xpath(
                    f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/i')

            except:
                if '0x00000000000000000000000' not in browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/a').text:
                    topHolderPercentage = browser.find_element_by_xpath(
                        f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[4]').text
                    break

        # browser.get(f'https://charts.bogged.finance/?token={contract}')
        # time.sleep(12)

        # marketcap = ''
        # liquidity = ''
        # twenty4HrVol = ''
        # price = ''
        # twenty4HrChange = ''

        # try:
        #     marketcap = browser.find_element_by_xpath(
        #         '/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[2]/span[3]/h4').text
        #     liquidity = browser.find_element_by_xpath(
        #         '/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[2]/span[2]/h4').text
        #     twenty4HrVol = browser.find_element_by_xpath(
        #         '/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[2]/span[1]/h4').text
        #     price = browser.find_element_by_xpath(
        #         '/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[1]/span[2]/h4').text
        #     twenty4HrChange = browser.find_element_by_xpath(
        #         '/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[1]/span[3]/h4').text
        # except:
        #     print(' ')

        bscLink = 'https://bscscan.com/token/' + contract
        poocoinLink = 'https://poocoin.app/tokens/' + contract
        boggedLink = 'https://charts.bogged.finance/?token=' + contract
        pancakeswap = 'https://exchange.pancakeswap.finance/#/swap?inputCurrency=' + contract

        # coins[contract].extend((numOfHolders, topHolderPercentage, top10Holders, top10Transfers, liquidity, marketcap,
        #                         twenty4HrVol, twenty4HrChange, lastTransaction, price, bscLink, boggedLink, poocoinLink, pancakeswap))

        coins[contract].extend((numOfHolders, topHolderPercentage, top10Holders, transfersInLastMin,
                                bscLink, boggedLink, poocoinLink, pancakeswap))

        browser.close()

    for key in list(coins):
        if key in records:
            del coins[key]

    writer = csv.writer(file)
    writer.writerow(['Name', 'Ticker', 'Holders', 'Top Whale (%)', 'Average Holding of Top 10 Whales (%)', 'Transfers in Last 1 Minute',
                     'BSCScan Link', 'Bogged Charts Link', 'Poocoin Charts Link', 'Buy on PancakeSwap Now'])
    for key, value in coins.items():
        writer.writerow(metric for metric in value)

    for key in list(coins):
        records[key] = coins[key]

    writer.writerow([' '])
    writer.writerow([' ', ' ', ' ', f'BEP-20 Transfers Page {page}'])
    writer.writerow([' '])

    browser.switch_to.window(browser.window_handles[0])
    browser.switch_to.default_content()
    nextPage = browser.find_element_by_xpath(
        '//*[@id="content"]/div[2]/div/div/div[1]/nav/ul/li[4]/a')
    nextPage.click()


file.close()
