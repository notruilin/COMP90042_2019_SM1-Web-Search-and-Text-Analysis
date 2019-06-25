"""
Created on Sat May 25 19:14:05 2019

Use to query doc by lupyne index, then resort sentences by a new in-memory index
"""

import time
import json
import lucene
import nltk
from org.apache.lucene import queryparser, analysis
from org.apache.lucene.search.similarities import BM25Similarity
from lupyne import engine

start_time = time.time()

lucene.initVM()
dest = "lucene_wikis.index"
indexer = engine.Indexer(dest)
indexer.setSimilarity(BM25Similarity())
analyzer = analysis.standard.StandardAnalyzer()
parser = queryparser.classic.QueryParser("text", analyzer)
prediction = {}
word_tokenizer = nltk.tokenize.regexp.WordPunctTokenizer()
nltk.download('averaged_perceptron_tagger')
related_sentences = []

def re_process_string(str):
    str = str.replace(" ", "_")
    str = str.replace("(", "-LRB-")
    str = str.replace(")", "-RRB-")
    return str

def get_related_docs(claim, field_name, num):
    if claim == "": return
    return indexer.search(claim,field=field_name,count=num)

def add_prediction(id, claim, sentences, label):
    prediction[id] = {}
    prediction[id]["claim"] = claim
    prediction[id]["label"] = "SUPPORTS"
    prediction[id]["label"] = label
    prediction[id]["evidence"] = []
    for sentence in sentences:
        # some wikis are invalid, e.g. The third sentence of "Matthew_Quick" doesn't have a sentence num
        if sentence[1].isdigit():
            prediction[id]["evidence"].append([re_process_string(sentence[0]), int(sentence[1])])
            #print(sentence[0][0], sentence[1])

def extract_title_NN(tokens_tags):
    NNs = []
    for i in range(len(tokens_tags)):
        if tokens_tags[i][1].startswith("VB"):   break
        if tokens_tags[i][0].isalnum():
            NNs.append(tokens_tags[i][0])
    query = " ".join(NNs)
    return query

def extract_last_NN(tokens_tags):
    NNs = []
    for i in range(len(tokens_tags) - 1, -1, -1):
        if tokens_tags[i][1].startswith("VB"):   break
        if tokens_tags[i][0].isalnum() and tokens_tags[i][1].startswith("NN"):
            NNs.insert(0, tokens_tags[i][0])
    query = " ".join(NNs)
    return query

def process_query(claim):
    query = ""
    if claim != "":
        query = parser.parse(queryparser.classic.QueryParser.escape(claim))
    return query

def escape_query(claim):
    query = ""
    if claim != "":
        query = queryparser.classic.QueryParser.escape(claim)
    return query

def add_to_related_docs(hit):
    related_sentences.append((hit["title"], hit["text"]))

def extract_sentences_as_docs(related_docs):
    docs = {}
    for doc in related_docs[1:]:
        sentences = doc[1].split("\n")
        title = doc[0]
        for sentence in sentences:
            id_sentence = sentence.split(" ", 1)
            if len(id_sentence) == 2 and id_sentence[0].isdigit():
                docs[(doc[0], id_sentence[0])] = title + " " + id_sentence[1]
    return docs

def sort_sentences(claim):
    docs = extract_sentences_as_docs(related_sentences)
    
    sentence_indexer = engine.Indexer()
    sentence_indexer.deleteAll()
    sentence_indexer.set('title', engine.Field.Text, stored = True)
    sentence_indexer.set('sen_id', engine.Field.Text, stored = True)
    sentence_indexer.set('text', engine.Field.Text, stored = True)
    
    for key, text in iter(docs.items()):
        title = key[0]
        sen_id = key[1]
        sentence_indexer.add(title = title, sen_id = sen_id, text = title + " " + text)
    sentence_indexer.commit()
    
    query = process_query(claim)
    hits = sentence_indexer.search(query, field='text',count=5)
    sentences = []
    for hit in hits:
        sentences.append((hit['title'],hit['sen_id']))
    sentence_indexer.deleteAll()
    sentence_indexer.commit()
    sentence_indexer.close()
    return sentences

# test-unlabelled.json   train.json   devset.json
with open("devset.json") as train_json:
    train_set = json.load(train_json)

tmp = 0
for data in train_set.items():
    tmp += 1
    print(tmp)
    claim = data[1]["claim"];
    label = data[1]["label"];
    tokens = word_tokenizer.tokenize(claim)
    tokens_tags = nltk.pos_tag(tokens)
    title_hit = get_related_docs(escape_query(extract_title_NN(tokens_tags)), "title", 2)
    NN_hits = get_related_docs(escape_query(extract_last_NN(tokens_tags)), "title", 2)
    claim_hits = get_related_docs(process_query(claim), "text", 5)
    related_docs = []
    
    for hits in [title_hit, NN_hits, claim_hits]:
        if hits != None:
            for hit in hits:
                add_to_related_docs(hit)
    
    sentences = sort_sentences(claim)
    
    add_prediction(data[0], claim, sentences, label)
    
    #add_sentence_prediction(data[0], claim, claim_hits)
    #if tmp == 10: break

# ir_train_output.json   ir_dev_output.json   ir_test-unlabelled.json
with open("ir_dev_output.json", "w") as outfile:
    json.dump(prediction, outfile, indent = 2)

if indexer != None:
    indexer.close()

end_time = time.time()
print()
print("Execution time: ", "%.2f" % (end_time - start_time) + " s")