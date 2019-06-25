"""
Created on Thu May 23 17:50:31 2019

Use to retrieve the sentences by wiki name and sentence id, then format all sentences of each claim into a jsonl
The jsonl output will is used to train and test NLP model
"""

import json
import random
import string

def process_i(s):
    s = s.replace("í", "i")
    s = s.replace("í", "i")

wikis = {}
for num in range(1, 110):
    file_num = str(num).zfill(3)
    with open("wiki-pages-text/wiki-" + file_num + ".txt") as f:
        for line in f:
            contents = line.split(" ", 2)
            if len(contents) != 3:  continue
            title = contents[0]
            sen_id = contents[1]
            text = contents[2]
            wikis[(process_i(title), sen_id)] = text
print("Dictionary complete!")
translator = str.maketrans(string.punctuation, " " * len(string.punctuation))

def get_random_evidence():
    random_text = []
    for i in range(5):
        random_text.append(random.choice(list(wikis.values())))
    return " ".join(random_text)

def process_string(str):
    str = str.replace("_", " ")
    str = str.replace("-LRB-", "(")
    str = str.replace("-RRB-", ")")
    str = str.translate(translator)
    return str.lower()

# ir_train_output.json   ir_dev_output.json   ir_test-unlabelled.json
with open("ir_dev_output.json") as train_json:
    train_set = json.load(train_json)
    print("train_set loaded!")
    tmp = 0
    data_set = []
    for data in train_set.items():
        tmp += 1
        print("num: ", tmp)
        claim = data[1]["claim"]
        if "label" in data[1]:
            label = data[1]["label"]
        else:
            label = None
        evidences = data[1]["evidence"]
        evi_text = []
        for evidence in evidences:
            title = evidence[0]
            sen_id = evidence[1]
            text = title + " "
            text += wikis[(process_i(title), str(sen_id))]
            evi_text.append(text)
        evi_text = process_string(" ".join(evi_text))
        #print(evi_text)

        if label == "NOT ENOUGH INFO":
            evi_text = get_random_evidence()
            print(evi_text)
        
        data_one = {}
        data_one["claim"] = claim
        data_one["evidence"] = evi_text
        if label:
            data_one["label"] = label
        
        data_set.append(data_one)
        #if tmp == 5: break

# train_evidence.jsonl   dev_evidence.jsonl   test_evidence.jsonl
with open("tmp_dev_evidence.jsonl", mode='a') as out_file:
    for line in data_set:
        json.dump(line, out_file)
        out_file.write('\n')

