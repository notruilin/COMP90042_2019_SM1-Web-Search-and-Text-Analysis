"""
Created on Thu May 16 15:01:09 2019

Use to query evidence by lupyne index
"""

import time
import json
import lucene
import nltk
import SortSens
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
related_docs = []

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
    if label:
        prediction[id]["label"] = label
    prediction[id]["evidence"] = []
    for sentence in sentences:
        # some wikis are invalid, e.g. The third sentence of "Matthew_Quick" doesn't have a sentence num
        if sentence[0][1].isdigit():
            prediction[id]["evidence"].append([re_process_string(sentence[0][0]), int(sentence[0][1])])
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
    related_docs.append((hit["title"], hit["text"]))

def sort_sentences(claim):
    vocabulary = SortSens.extract_vocabulary(related_docs, claim)
    primary_sense = SortSens.get_primary_sense(vocabulary)
    docs = SortSens.extract_sentences_as_docs(related_docs)
    docs_term_freqs = SortSens.count_term_freqs_for_all_docs(docs)
    doc_freqs = SortSens.count_doc_freqs(docs_term_freqs)
    inverted_index = SortSens.build_inverted_index(docs_term_freqs, doc_freqs)
    query = SortSens.extract_terms_from_doc(claim)
    sentences = SortSens.query_topk_sentences(query, inverted_index, 5, vocabulary, primary_sense)
    return sentences

# test-unlabelled.json   train.json   devset.json
with open("devset.json") as train_json:
    train_set = json.load(train_json)

tmp = 0
for data in train_set.items():
    tmp += 1
    print(tmp)
    claim = data[1]["claim"];
    label = None
    if "label" in data[1]:
        label = data[1]["label"];
    tokens = word_tokenizer.tokenize(claim)
    tokens_tags = nltk.pos_tag(tokens)
    title_hit = get_related_docs(escape_query(extract_title_NN(tokens_tags)), "title", 1)
    last_hit = get_related_docs(escape_query(extract_last_NN(tokens_tags)), "title", 1)
    claim_hits = get_related_docs(process_query(claim), "text", 3)
    related_docs = []
    
    for hits in [title_hit, last_hit, claim_hits]:
        if hits != None:
            for hit in hits:
                add_to_related_docs(hit)
    """
    if tmp == 5:
        print("title_hit:")
        for hit in title_hit:
            print(hit["title"], hit.score)
        print("last_hit:")
        for hit in last_hit:
            print(hit["title"], hit.score)
        print("claim_hits:")
        for hit in claim_hits:
            print(hit["title"], hit.score)
        print("DOCS:")
        for doc in related_docs:
            print(doc[0])
    """
    sentences = sort_sentences(claim)
    """
    if tmp == 5:
        print("SENTENCE:")
        print(sentences)
    """
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