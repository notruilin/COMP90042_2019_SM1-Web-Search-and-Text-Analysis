
"""
Created on Tue May 14 19:29:52 2019

Use to create lupyne index
"""

import time
import lucene
from lupyne import engine

start_time = time.time()

lucene.initVM()
dest = "lucene_wikis_sentences.index"
indexer = engine.Indexer(dest)
indexer.set('title', engine.Field.Text, stored = True)
indexer.set('sen_id', engine.Field.Text, stored = True)
indexer.set('text', engine.Field.Text, stored = True)

def process_string(str):
    str = str.replace("_", " ")
    str = str.replace("-LRB-", "(")
    str = str.replace("-RRB-", ")")
    return str

for num in range(1, 110):
    file_num = str(num).zfill(3)
    print("Processing " + "wiki-pages-text/wiki-" + file_num + ".txt...")
    with open("wiki-pages-text/wiki-" + file_num + ".txt") as f:
        for line in f:
            contents = line.split(" ", 2)
            if len(contents) != 3:  continue
            title = contents[0]
            sen_id = contents[1]
            text = contents[2]
            title = process_string(title)
            text = process_string(text)
            indexer.add(title = title, sen_id = sen_id, text = title + " " + text)
indexer.commit()

end_time = time.time()
print("Execution time: ", "%.2f" % (end_time - start_time) + " s")

hits = indexer.search('The 19th G7 summit only included Russia.',field='text',count=20)
print("The 19th G7 summit only included Russia.: ", hits.count)
for hit in hits:
    print(hit['title'])
    
if indexer != None:
    indexer.close()