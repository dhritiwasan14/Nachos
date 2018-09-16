from pymongo import MongoClient

client = MongoClient()

client = MongoClient('localhost', 27017)

mydb = client.test_database_1
