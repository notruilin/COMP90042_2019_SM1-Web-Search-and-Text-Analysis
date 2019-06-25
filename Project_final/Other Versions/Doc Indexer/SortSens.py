"""
Created on Sat May 18 17:15:24 2019

Use to rank the top k sentence by tf-idf
Reference: WSTA_N2_information_retrieval.ipynb
"""

import nltk
import math
from nltk.corpus import wordnet
from collections import defaultdict, Counter

nltk.download('stopwords')
nltk.download('wordnet')
stopwords = set(nltk.corpus.stopwords.words("english"))
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
# stemmer = nltk.stem.PorterStemmer()

def lemmatize(word):
    lemma = lemmatizer.lemmatize(word,'v')
    if lemma == word:
        lemma = lemmatizer.lemmatize(word,'n')
    return lemma

def get_sense_count(synset, word):
    #print("synset: ", synset, "word: ", word)
    for lemma in synset.lemmas():
        if lemma.name().lower() == word.lower():
            return lemma.count()
    return 0

def get_most_common_sense(word):
    most_common = None
    max_count = -1
    for synset in wordnet.synsets(word):
        count = get_sense_count(synset, word)
        if max_count < count:
            max_count = count
            most_common = synset
    return most_common

def get_synonyms(term, vocabulary, primary_sense):
    words = []
    for synonym in vocabulary:
        if synonym != term and primary_sense[term] and primary_sense[synonym] and primary_sense[term].wup_similarity(primary_sense[synonym]) and primary_sense[term].wup_similarity(primary_sense[synonym]) > 0.7:
            words.append(synonym)
    return words

def get_primary_sense(vocabulary):
    primary_sense = {}
    for term in vocabulary:
        primary_sense[term] = get_most_common_sense(term)
    return primary_sense

def extract_terms_from_doc(doc):
    terms = set()
    for token in nltk.word_tokenize(doc):
        if token not in stopwords:
            terms.add(lemmatize(token.lower()))
    return terms

def extract_vocabulary(related_docs, claim):
    vocabulary = set()
    for doc in related_docs:
        vocabulary = vocabulary.union(extract_terms_from_doc(doc[1]))
    vocabulary = vocabulary.union(extract_terms_from_doc(claim))
    #print(vocabulary)
    return vocabulary

def extract_sentences_as_docs(related_docs):
    docs = {}
    for doc in related_docs:
        sentences = doc[1].split("\n")
        title = doc[0]
        for sentence in sentences:
            id_sentence = sentence.split(" ", 1)
            if len(id_sentence) == 2 and id_sentence[0].isdigit():
                docs[(doc[0], id_sentence[0])] = extract_terms_from_doc(title + " " + id_sentence[1])
    return docs

def count_term_freqs(terms):
    term_freqs = Counter()
    for term in terms:
        term_freqs[term] += 1
    return term_freqs

def count_term_freqs_for_all_docs(docs):
    docs_term_freqs = defaultdict(Counter)
    for key, terms in iter(docs.items()):
        docs_term_freqs[key] = count_term_freqs(terms)
    return docs_term_freqs

def count_doc_freqs(docs_term_freqs):
    doc_freqs = Counter()
    for counter in docs_term_freqs.values():
        for term in counter.keys():
            doc_freqs[term] += 1
    return doc_freqs

def build_inverted_index(docs_term_freqs, doc_freqs):
    inverted_index = defaultdict(list)
    docs_num = len(docs_term_freqs)
    for key, term_freqs in docs_term_freqs.items():
        length = 0
        
        weights = []
        for term, term_num in term_freqs.items():
            if term_num == 0 or doc_freqs[term] == 0 or docs_num == doc_freqs[term]:
                tfidf = 0
            else:
                tfidf = float(term_num) / math.log(docs_num / float(doc_freqs[term]))
            length += tfidf ** 2
            weights.append((term, tfidf))
        
        length = length ** 0.5
        for term, w in weights:
            if length == 0:
                value = 0
            else:
                value = w / length
            inverted_index[term].append([key, value])
    
    for term, key in inverted_index.items():
        key.sort()
        
    return inverted_index

def query_topk_sentences(query, inverted_index, k, vocabulary, primary_sense):
    accumulators = Counter()
    for term in query:
        #print("term: ", term)
        for synonym in get_synonyms(term, vocabulary, primary_sense):
            #print("synonym: ", synonym)
            posting_list = inverted_index[synonym]
            for key, w in posting_list:
                accumulators[key] += w
        posting_list = inverted_index[term]
        for key, w in posting_list:
            accumulators[key] += w
    return accumulators.most_common(k)
        