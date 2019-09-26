from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import os
import time

def order():
    driver = webdriver.Chrome('./chromedriver.exe')
    driver.get('https://www.google.com/')
    time.sleep(3)
    driver.find_element_by_xpath("//input[@title='Search']").send_keys("car")
    #time.sleep(1)
    #driver.get('https://www.youtube.com/')

if __name__ == '__main__':
	order()