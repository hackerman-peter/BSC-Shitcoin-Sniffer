from selenium import webdriver
import time
import math
from datetime import datetime
import csv


browser = webdriver.Chrome('./chromedriver')
browser.maximize_window()

browser.get('https://bscscan.com/tokentxns')

# Get length of row in one page
rows = len(browser.find_elements_by_xpath('//*[@id="content"]/div[2]/div/div/div[2]/table/tbody/tr'))

coins = {}
bscscanLinkCount = 1
boggedLinkCount = 0
for r in range(1, rows + 1):
    coinXPath = '//*[@id="content"]/div[2]/div/div/div[2]/table/tbody/tr[' + str(r) + ']/td[9]/a'

    # If not new coin image (grey), then skip it
    imageSource = browser.find_element_by_xpath(coinXPath + '/img').get_attribute('src')
    if imageSource != 'https://bscscan.com/images/main/empty-token.png':
        continue

    # Getting coin name and ticket symbol
    coinElement = browser.find_element_by_xpath(coinXPath)
    ticker = coinElement.text[coinElement.text.find("(") + 1:coinElement.text.find(")")]
    name = coinElement.text

    # Getting link for coins and opening it
    bscLink = browser.find_element_by_xpath(coinXPath).get_attribute('href')
    # Getting contract
    contract = bscLink.replace('https://bscscan.com/token/', '')

    # Appending everything into a dictionary
    coinInfo = [name, ticker, bscLink]
    coins[contract] = coinInfo

# Opening tabs
for contract in coins:
    browser.execute_script('window.open("' + coins[contract][2] + '","_blank");')
    bscscanLinkCount += 1


# Transfers and holders information
for i in range(1, bscscanLinkCount):
    browser.switch_to.window(browser.window_handles[-1])

    print("Currently on: " + browser.title)

    contract = browser.current_url.replace('https://bscscan.com/token/', '')
    print(contract)

    # Get the tokens list iframe and switch to it
    iframe = browser.find_element_by_xpath('//*[@id="tokentxnsiframe"]')
    browser.switch_to.frame(iframe)

    # Now you can go through each transfer directly
    top10Transfers = 0
    transferLength = len(browser.find_elements_by_xpath('//*[@id="maindiv"]/div[2]/table/tbody/tr'))
    if 10 < transferLength:
        for transferNum in range(1, 10+1):
            transfer = browser.find_element_by_xpath(f'//*[@id="maindiv"]/div[2]/table/tbody/tr[{transferNum}]/td[3]/span')
            transfer = transfer.text.replace(' ago', '')

            # Standardise transfer time to seconds
            if 'secs' in transfer:
                transfer = int(transfer.split()[0])
            elif 'mins' in transfer or 'min' in transfer:
                transfer = int(transfer.split()[0]) * 60
            elif ('hours' in transfer or 'hour' in transfer) and 'day' not in transfer:
                transfer = int(transfer.split()[0]) * 60 * 60
            elif 'day' in transfer:
                transfer = int(transfer.split()[0]) * 60 * 60 * 24
            elif 'hours' in transfer and 'day' in transfer:
                transfer = (int(transfer.split()[0]) * 60 * 60 * 24) + (int(transfer.split()[2])  * 60 * 60)
    else:
        for transferNum in range(1, transferLength):
            transfer = browser.find_element_by_xpath(
                f'//*[@id="maindiv"]/div[2]/table/tbody/tr[{transferNum}]/td[3]/span')
            transfer = transfer.text.replace(' ago', '')

            # Standardise transfer time to seconds
            if 'secs' in transfer:
                transfer = int(transfer.split()[0])
            elif 'mins' in transfer or 'min' in transfer:
                transfer = int(transfer.split()[0]) * 60
            elif ('hours' in transfer or 'hour' in transfer) and 'day' not in transfer:
                transfer = int(transfer.split()[0]) * 60 * 60
            elif 'day' in transfer:
                transfer = int(transfer.split()[0]) * 60 * 60 * 24
            elif 'hours' in transfer and 'day' in transfer:
                transfer = (int(transfer.split()[0]) * 60 * 60 * 24) + (int(transfer.split()[2]) * 60 * 60)
    top10Transfers = transfer / 10


    # Normalise time back to secs/mins/hours/days
    if top10Transfers < 60:
        top10Transfers = str(top10Transfers) + ' secs'
    elif 60 <= top10Transfers < (60 * 60):
        top10Transfers = str(top10Transfers/60) + ' mins'
    elif (60 * 60) <= top10Transfers < (60 * 60 * 24):
        top10Transfers = str(top10Transfers/(60 * 60)) + ' hours'
    elif top10Transfers >= (60 * 60 * 24):
        decimal = top10Transfers % 1
        top10Transfers = str(math.floor(top10Transfers/(60 * 60 * 24))) + ' days'
        if decimal > 0:
            top10Transfers += ' ' + str(decimal * 60 * 60) + ' hours'

    coins[contract].append(top10Transfers)

    # Getting the first transaction from the last page of all transactions
    try:
        lastTransactionPage = browser.find_element_by_xpath('//*[@id="maindiv"]/div[1]/nav/ul/li[5]/a')
        lastTransactionPage.click()
    except:
        print('first page is also the last page')

    browser.switch_to.default_content()
    browser.switch_to.frame(iframe)

    # Getting the length of transactions on the last page
    lastTransactionPageRowLength = len(browser.find_elements_by_xpath('//*[@id="maindiv"]/div[2]/table/tbody/tr'))
    lastTransaction = browser.find_element_by_xpath(f'//*[@id="maindiv"]/div[2]/table/tbody/tr[{lastTransactionPageRowLength}]/td[3]/span').text

    coins[contract].append(lastTransaction)


    # Getting holder information
    browser.switch_to.default_content()

    holdersTab = browser.find_element_by_xpath('//*[@id="ContentPlaceHolder1_tabHolders"]')
    holdersTab.click()

    iframe = browser.find_element_by_xpath('//*[@id="tokeholdersiframe"]')
    browser.switch_to.frame(iframe)

    top10Holders = 0.0
    holderLength = len(browser.find_elements_by_xpath('//*[@id="maintable"]/div[3]/table/tbody/tr'))
    if 10 < holderLength:
        for i in range(1,  10 + 1):

            try:
                browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/i')
            except:
                holderPercentage = browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[4]')
                holderPercentage = holderPercentage.text.replace('%', '')
                top10Holders += float(holderPercentage)

            i += 1

    else:
        for i in range(1, holderLength + 1):

            try:
                browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/i')
            except:
                holderPercentage = browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[4]')
                holderPercentage = holderPercentage.text.replace('%', '')
                top10Holders += float(holderPercentage)

            i += 1

    top10Holders /= holderLength

    # Getting top holder
    topHolderPercentage = ''
    for i in range(1, holderLength + 1):
        try:
            browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[2]/span/i')
        except:
            topHolderPercentage = browser.find_element_by_xpath(f'//*[@id="maintable"]/div[3]/table/tbody/tr[{str(i)}]/td[4]').text
        i += 1

    coins[contract].append(topHolderPercentage)

    browser.get(f'https://charts.bogged.finance/?token={contract}')
    time.sleep(12)

    marketcap = ''
    liquidity = ''
    twenty4HrVol = ''
    price = ''
    twenty4HrChange = ''

    try:
        marketcap = browser.find_element_by_xpath('/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[2]/span[3]/h4').text
        liquidity = browser.find_element_by_xpath('/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[2]/span[2]/h4').text
        twenty4HrVol = browser.find_element_by_xpath('/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[2]/span[1]/h4').text
        price = browser.find_element_by_xpath('/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[1]/span[2]/h4').text
        twenty4HrChange = browser.find_element_by_xpath('/html/body/div/div[2]/main/div/div/div/div/div[1]/div[1]/div[1]/span[3]/h4').text
    except:
        print('bsc issue')

    print('Price ==' + price)
    coins[contract].extend((price, marketcap, liquidity, twenty4HrVol, twenty4HrChange))

    browser.close()

print(coins)
csvFileName = str(datetime.now()) + '.csv'
file = open(csvFileName, "w")

writer = csv.writer(file)
writer.writerow(['Name', 'Ticker', 'BSCLink', 'Average 10 Recent Transfers', 'Coin Launch', 'Top 10 Holders %', 'Price', 'MarketCap', 'Liquidity', '24 Hours Volume', '24 Hours Change %'])
for key, value in coins.items():
    writer.writerow(metric for metric in value)

file.close()







