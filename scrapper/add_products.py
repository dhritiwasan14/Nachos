import json
import requests

from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.nachos

with open('catalogue.json', 'r') as f:
    product_dict = json.load(f)

    products = db.products
    count = 1
    for k, v in product_dict.items():
        post_data = {
            'id': count,
            'name': k, 
            'content': v['description'],
            'category': v['category'][1:],
            'price': v['price'],
            'miles': v['miles'],
            'image': v['image_source']
        }
        count+=1
        print (post_data)
        r = requests.post("http://localhost:5000/add_product", data=post_data)
        print (r)
        