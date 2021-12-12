import json
import jieba
import logging
import pymongo as mg
from collections import Counter

log_file = './db.log'
stop_words = './data/stop_words.txt'
vocab_file = './data/vocab.txt'
vocab_idf_file = './data/vocab_idf.txt'
original_document_file = './data/original_document.json'

client = mg.MongoClient('localhost', 27017)
db = client["music"] # create a music database
logging.basicConfig(level=logging.INFO, filename=log_file, filemode='w', format='%(asctime)s - %(levelname)s: %(message)s')

original_document = db["original_document"] # create a orginal_document collection
# ! deprecated
# word2id = db["word2id"] # create a word2id collection
# id2word = db["id2word"] # create a id2word collection
singer2doc_id = db["singer2doc_id"] # create a singer2doc_id collection
song2doc_id = db["song2doc_id"] # create a song2doc_id collection
word2doc_id = db["word2doc_id"] # create a word2doc_id collection

# load stop words
with open(stop_words, 'r', encoding='utf-8') as f:
    stop_words = f.read().splitlines()
logging.info('stop words loaded')

# analysis original json file
original_json = []
doc_num = 0
with open(original_document_file, "r") as f:
    for line in f:
        original_json.append(json.loads(line))
        doc_num += 1
logging.info('original document loaded')

for song in original_json:
    document = {
        "artist": song["singer"],
        "title": song["song"],
        "lyric": song["geci"],
        "composer": song["composer"],
        "author": song["author"],
        "album": song["album"],
    }
    original_document.insert_one(document)
logging.info('original document collection created')

# * process lyric
wordCounter = Counter() # counte word frequency in all documents
wordDF = Counter() # counte word document frequency
for song in db.original_document.find():
    word_set = set()
    for sent in song["lyric"]:
        for word in jieba.cut(sent):
            # skip stop words
            if word in stop_words:
                continue
            wordCounter[word] += 1
            word_set.add(word)
    for word in word_set:
        wordDF[word] += 1
logging.info('word counter created')

# create file of term frequency
with open(vocab_idf_file, "w") as f:
    for word, count in wordDF.most_common():
        f.write('%s %.4f\n' % (word, doc_num/count))

# create file of vocab2id
with open(vocab_file, "w") as f:
    token = 100 # id less than 100 reserved for special tokens
    for word, count in wordCounter.most_common():
        f.write('%s %d\n' % (word, token))
        token += 1

logging.info('vocab.txt and vocab_idf.txt created')

# ! deprecated
# # create word2id and id2word collections
# with open(vocab_file, "r") as f:
#     for line in f:
#         try:
#             word, id = line.strip().split()
#         except:
#             logging.error('line: ' + line)
#         word2id.insert_one({"word": word, "id": int(id)})
#         id2word.insert_one({"id": int(id), "word": word})
# logging.info('word2id and id2word collections created')

# create word2doc_id, song2doc_id and singer2doc_id collections
w2d, song2d, singer2d = {}, {}, {}
for song in db.original_document.find():
    wordTF = Counter()
    for sent in song["lyric"]:
        for word in jieba.cut(sent):
            if word in stop_words:
                continue
            wordTF[word] += 1
    # ! str occupy more space than ObjectId
    for word, count in wordTF.most_common():
        # TODO word2<doc_id, tf>
        w2d[word] = w2d.get(word, []) + [(song["_id"], count)]
    song2d[song["title"]] = song2d.get(song["title"], []) + [song["_id"]]
    singer2d[song["artist"]] = singer2d.get(song["artist"], []) + [song["_id"]]

# insert to collections one by one
for key, value in w2d.items():
    word2doc_id.insert_one({"word": key, "doc_id&TF": value})
for key, value in song2d.items():
    song2doc_id.insert_one({"song": key, "doc_id": value})
for key, value in singer2d.items():
    singer2doc_id.insert_one({"singer": key, "doc_id": value})
logging.info('word2doc_id, song2doc_id and singer2doc_id collections created')

logging.info('createDB.py finished')