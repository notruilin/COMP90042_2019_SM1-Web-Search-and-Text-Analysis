"""
Created on Thu May 23 23:08:54 2019

Format the final output json
"""

import json
from collections import OrderedDict
from collections import Counter
from itertools import islice

# ir_test-unlabelled.json   ir_dev_output.json
with open("ir_test-unlabelled.json") as test_json:
    test_set = json.load(test_json, object_pairs_hook = OrderedDict)
print("testoutput load!")

def get_label(labels):
    cnt = Counter()
    for label in labels:
        cnt[label] += 1
    if cnt.most_common(1)[0][0] == "NOT ENOUGH INFO" and len(set(labels)) > 1:
        print("top2: ", cnt.most_common(2))
        print("label: ", cnt.most_common(2)[1][0])
        return cnt.most_common(2)[1][0]
    return cnt.most_common(1)[0][0]

def get_next_n_lines(file, n):
    return [line.strip() for line in islice(file, n)]

test_list = list(test_set.keys())

# outputPredictions.json dev_outputPredictions.json
with open("outputPredictions.json") as label_output:
    for i in range(len(test_set)):
        print(i)
        num = len(test_set[test_list[i]]["evidence"])
        lines = get_next_n_lines(label_output, num)
        labels = []
        
        if num == 0:
            test_set[test_list[i]]["label"] = "NOT ENOUGH INFO"
            continue
        
        for line in lines:
            data = json.loads(line)
            labels.append(data["label"])
        final_label = get_label(labels)

        new_evi = []
        evidences = test_set[test_list[i]]["evidence"]
        j = 0
        for line in lines:
            data = json.loads(line)
            if data["label"] == final_label:
                new_evi.append(evidences[j])
            j += 1

        test_set[test_list[i]]["label"] = final_label

        if len(test_set[test_list[i]]["evidence"]) != len(new_evi):
            print("hahahahaha")
        test_set[test_list[i]]["evidence"] = new_evi

        if final_label == "NOT ENOUGH INFO":
            test_set[test_list[i]]["evidence"] = []  
        #if i == 7: break
    
# testoutput.json   devoutput.json
with open("testoutput.json", "w") as outfile:
    json.dump(test_set, outfile, indent = 2)
