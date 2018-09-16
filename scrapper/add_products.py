import json

from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.nachos

with open('catelog_data.json', 'r') as f:
    product_dict = json.load(f)

    products = db.products
    for k, v in product_dict.items():
        post_data = {
            'name': k, 
            'content': v['descr']
        }