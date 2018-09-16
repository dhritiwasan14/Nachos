import requests
import json
from bs4 import BeautifulSoup

catelog = dict()

def parser(link, dictionary = catelog):
    page = requests.get(link)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Getting the lists for the relevant attributes
    div_list = soup.find_all('div', class_ = "")
    h3_list = soup.find_all('h3')
    img_list = soup.find_all('img')

    #Hackish way of accessing it

    product_description = div_list[6].get_text().strip()
    product_img = img_list[-2]["src"]
    product_title = h3_list[4].get_text()
    price = h3_list[5].get_text()
    miles = h3_list[6].get_text()
    category = soup.find_all('ol', class_="breadcrumb")[0].get_text().split('\n')[1:-1]

    catelog[product_title] = dict(
                        cateogry = category,
                        description = product_description,
                        price = price,
                        miles = miles,
                        image_source = product_img)




#
link1 = "https://www.krisshopair.com/product_info.aspx?pid=45515A41555946555040505C4957303D262B3E2F"
link2 = "https://www.krisshopair.com/product_info.aspx?pid=45515A4155554657504750594C502D2753392059"

link3 = "https://www.krisshopair.com/product_info.aspx?pid=45515A41555445545046505D4D57363E3239312B"
link4 = "https://www.krisshopair.com/product_info.aspx?pid=45515A41555544555041545B4851333E2B283627"

links = [link1, link2, link3, link4]

for link in links:
    parser(link)
    with open("catelog_data.json", "w") as write_file:
        json.dump(catelog, write_file)

#
# page = requests.get(link4)
# print("requests is: {} ".format(page))
# soup = BeautifulSoup(page.content, 'html.parser')
#
#
# category = soup.find_all('ol', class_="breadcrumb")[0].get_text().split('\n')[1:-2]

# print(li_list)
# div_list = soup.find_all('div', class_ = "")
# h3_list = soup.find_all('h3')
# img_list = soup.find_all('img')
#
#
# product_description = div_list[6].get_text().strip()
# # print(product_description)
#
# product_img = img_list[-2]["src"]
# print(product_img)
#
# product_title = h3_list[4].get_text()
# print(product_title)
# price = h3_list[5].get_text()
# print(price)
# miles = h3_list[6].get_text()
# print(miles)
#


