import re
import pymongo as mg

client = mg.MongoClient('localhost', 27017)
db = client["music"] # use music database

cnt = db.word2doc_id.count_documents({})

print(cnt)