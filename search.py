import time
import jieba
import logging
import pymongo as mg
# from bson.objectid import ObjectId

log_file = './search.log'

client = mg.MongoClient('localhost', 27017)
db = client["music"] # use music database
logging.basicConfig(level=logging.INFO, filename=log_file, filemode='a', format='%(asctime)s - %(levelname)s: %(message)s')

def display(result):
    for id in result['doc_id']:
        song = db.original_document.find_one({'_id': id})
        title = song['title']
        artist = song['artist']
        lyric = "\n".join(song['lyric'])
        print("%s: 《%s》" % (artist, title))
        # print("title: %s, artist: %s\nlyric: \n%s" % (title, artist, lyric))

def display2(results):
    for result in results:
        id = result[0]
        song = db.original_document.find_one({'_id': id})
        title = song['title']
        artist = song['artist']
        print("%s: 《%s》" % (artist, title))

while True:

    # load vocobulary idf
    vocab_idf_file = './data/vocab_idf.txt'
    vocab_idf = {}
    with open(vocab_idf_file, 'r') as f:
        for line in f:
            try:
                word, idf = line.strip().split()
                vocab_idf[word] = float(idf)
            except:
                logging.error('line: ' + line)

    topK = 10 # top 10 songs sorted by tf-idf

    print('Enter search term:')
    search_term = input()
    logging.info('Search term: ' + search_term)
    if search_term == 'exit':
        logging.info('Exiting program')
        break
    start = time.time()
    # Step 1: Check whether the search term is a song name
    count = db.song2doc_id.count_documents({"song": search_term})
    if count > 0:
        results = db.song2doc_id.find_one({"song": search_term})
        logging.info('Found %d songs', count)
        print('Found %d songs by title' % count)
        display(results)
    else:
        logging.info('No song found')

    # Step 2: If not, check whether the search term is a singer name
    count = db.singer2doc_id.count_documents({"singer": search_term})
    if count > 0:
        results = db.singer2doc_id.find_one({"singer": search_term})
        logging.info('Found %d songs', count)
        print('Found %d songs by artist' % count)
        display(results)
    else:
        logging.info('No singer found')

    # Step 3: If not, assume the search term is a lyric
    score = {}
    for word in jieba.cut(search_term):
        count = db.word2doc_id.count_documents({"word": word})
        if count > 0:
            result = db.word2doc_id.find_one({"word": word})
            for doc_id, tf in result['doc_id&TF']:
                # print(doc_id, tf)
                # print(type(doc_id))
                score[doc_id] = score.get(doc_id, 0) + 1 * vocab_idf.get(word, 0)
    results = sorted(score.items(), key=lambda x: x[1], reverse=True)[:topK]
    logging.info('Found %d songs by lyric', len(results))
    print('Found %d songs by lyric' % len(results))
    display2(results)

    print("Time cost: %.3fs" % (time.time() - start))