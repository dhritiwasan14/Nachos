import time
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


product_links = []

def get_links(link, cache = product_links):
    driver = webdriver.Chrome('/Users/new/Downloads/chromedriver_new')
    driver.get(link)

    time.sleep(5)
    continue_link = driver.find_element_by_tag_name("a")
    elems = driver.find_elements_by_xpath("//a[@href]")

    for elem in elems:
        link = elem.get_attribute("href")
        if "product_info" in link and link not in cache:
            # print(link)
            cache.append(link)


    driver.close()

for i in range(1,34):
    print(i)
    link = "https://www.krisshopair.com/products.aspx#!{}_-_0_0_40_00_".format(i)
    print(link)
    get_links(link, product_links)


print(len(product_links))
print(product_links)

# Writing the file
csvfile = "./links.csv"

with open(csvfile, "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for val in product_links:
        writer.writerow([val])
