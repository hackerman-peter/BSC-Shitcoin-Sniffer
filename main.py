from selenium import webdriver
import time
import math

browser = webdriver.Chrome('./chromedriver')
browser.maximize_window()

browser.get('https://bscscan.com/tokentxns')

# Get length of row in one page
rows = len(browser.find_elements_by_xpath('//*[@id="content"]/div[2]/div/div/div[2]/table/tbody/tr'))

coins = {}
linkCount = 1
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
    linkCount += 1

# Transfers
for i in range(1, linkCount):
    browser.switch_to.window(browser.window_handles[i])
    print("Currently on: " + browser.title)

    # Get the tokens list iframe and switch to it
    iframe = browser.find_element_by_xpath('//*[@id="tokentxnsiframe"]')
    browser.switch_to.frame(iframe)

    # Now you can go through each transfer directly
    top10Transfers = 0
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

    # Getting the first transaction from the last page of all transactions
    try:
        lastTransactionPage = browser.find_element_by_xpath('//*[@id="maindiv"]/div[1]/nav/ul/li[5]/a')
        lastTransactionPage.click()
    except:
        print('first page is also the last page')

    # After the last button is clicked, there is a delay before it actually
    # loads up the last page of transfers. 
    #
    # You can either use the hacky method of time.sleep(1) (which is not 
    # ideal), or you switch back to the parent iframe, then re-switch into the 
    # tokentxnsiframe. This will cause it to wait for the new iframe to load 
    # again. I'm using the second method here
    browser.switch_to.default_content()
    browser.switch_to.frame(iframe)

    # Getting the length of transactions on the last page
    lastTransactionPageRowLength = len(browser.find_elements_by_xpath('//*[@id="maindiv"]/div[2]/table/tbody/tr'))

    # Don't do `lastTransactionPageRowLength - 1`, the rows are indexed
    # starting from 1
    lastTransaction = browser.find_element_by_xpath(f'//*[@id="maindiv"]/div[2]/table/tbody/tr[{lastTransactionPageRowLength}]/td[3]/span')
    print(lastTransaction.text)
