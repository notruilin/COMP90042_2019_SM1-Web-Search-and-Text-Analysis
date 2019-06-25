"""
Created on Thu May 23 23:08:54 2019

Format the final output json
"""

import json
from collections import OrderedDict

# ir_test-unlabelled.json   ir_dev_output.json
with open("ir_test-unlabelled.json") as test_json:
    test_set = json.load(test_json, object_pairs_hook = OrderedDict)
print("testoutput load!")

test_list = list(test_set.keys())
id = 0
# outputPredictions.json devoutputPredictions.json
with open("outputPredictions.json") as label_output:
    for line in label_output:
        print(id)
        data = json.loads(line)
        label = data["label"]
        test_set[test_list[id]]["label"] = label
        if label == "NOT ENOUGH INFO":
            test_set[test_list[id]]["evidence"] = []
        id += 1
        #if id > 5: break
    
# testoutput.json   devoutput.json
with open("testoutput.json", "w") as outfile:
    json.dump(test_set, outfile, indent = 2)
