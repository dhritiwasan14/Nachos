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
                        category = category,
                        description = product_description,
                        price = price,
                        miles = miles,
                        image_source = product_img)



#
from csv_to_list import links_list as links
links = links[::10]
print("All the links are loaded")
print(len(links))

for i, link in enumerate(links):
    print(i+1)
    parser(link)

print("All the links have been parsed")

with open("catalogue.json", "w") as write_file:
    json.dump(catelog, write_file)

print(len(catelog))
