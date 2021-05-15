from selenium import webdriver
import time

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
    for transferNum in range(1, 10+1):
        transfer = browser.find_element_by_xpath(f'//*[@id="maindiv"]/div[2]/table/tbody/tr[{transferNum}]/td[3]/span')
        print(transfer.text)

    """
    # Just commenting this code out temporarily
    holders = browser.find_element_by_xpath('//*[@id="ContentPlaceHolder1_tr_tokenHolders"]/div/div[2]/div/div')

    transfersTab = browser.find_element_by_xpath('//*[@id="li_transactions"]/a')
    transfersTab.click()
    transfers = []

    for transferNum in range(1, 10):
        # transfer = browser.find_element_by_xpath('//*[@id="maindiv"]/div[2]/table/tbody/tr[' + str(transferNum) + ']/td[3]/span')
        transfer = browser.find_element_by_xpath('/html/body/div[2]/div[2]/table/tbody/tr[' + str(transferNum) + ']/td[3]/span')
        print(transfer.text)
        transfer = transfer.text.replace(' ago', '')
        print(transfer)
    """


