# LyricSearch

Hi, welcome to LyricSearch - a simple (Yes), fast (Maybe), and powerful (Approach) lyric search engine.

We support **Three** search methods to search songs:
1. Search by artist name.
2. Search by song name.
3. Search by lyrics. Fuzzy search is supported.

Issues and Forks are welcome.

# Dependencies
If you want to use the search engine, you need to install the dependencies first by run:

```cmd
pip install -r requirements.txt
```

Then run:
```cmd
python createDB.py
```
to create the database.

And finally, run:
```cmd
python search.py
```
to start the search engine.

The db_architecture.json shows the database architecture details.

We only upload the first 1000 lines of orginal document due to the file size limitation of github.

The full original document is available at: https://www.heywhale.com/mw/dataset/5e6382164b7a30002c98c62c