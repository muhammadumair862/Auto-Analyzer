from selenium import webdriver
from selenium.webdriver.chrome.options import Options as chromeoptions
from webdriver_manager.chrome import ChromeDriverManager

chrome_options=chromeoptions()
chrome_options.add_extension('ipburger.crx')

def upload_draft(filename):
    # driver=webdriver.Chrome("chromedriver.exe",options=chrome_options)
    driver = webdriver.Chrome(ChromeDriverManager().install())   #intialize webdriver
    driver.get("https://signin.ebay.com.au/ws/eBayISAPI.dll?SignIn&ru=https%3A%2F%2Fwww.ebay.com.au%2Fmyb%2FSummary")

    # username input
    driver.find_element_by_id('userid').clear()
    driver.find_element_by_id('userid').send_keys('super*_*deals')
    driver.find_element_by_id('signin-continue-btn').click()

    # password input
    driver.find_element_by_id('pass').clear()
    driver.find_element_by_id('pass').send_keys('EP@ge0221')
    driver.find_element_by_id('sgnBt').click()

    driver.get('https://www.ebay.com.au/sh/lst/active')
    driver.execute_script('document.getElementsByClassName("textual-display fake-link")[0].click()')
    # driver.find_element_by_class_name('btn btn--primary').click()
    driver.find_element_by_id('file-input').send_keys(r'C:\Users\Muhammad Umair\Downloads\ebay1.csv')