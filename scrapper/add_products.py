import json

from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client.nachos

with open('catelog_data.json', 'r') as f:
    product_dict = json.load(f)

    products = db.products
    count = 1
    for k, v in product_dict.items():
        post_data = {
            'id': count,
            'name': k, 
            'content': v['description'],
            'category': v['cateogry'][1:],
            'price': v['price'],
            'miles': v['miles'],
            'image': v['image_source']
        }
        count+=1
        product = products.insert_one(post_data)
        print('One post: {0}'.format(product.inserted_id))