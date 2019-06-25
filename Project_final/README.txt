Requirments: lupyne   pylucene   AllenNLP

For training:
1. Use IndexWikis.py to build a lupyne index
2. Use QueryWikis.py to query evidences for train.json and devset.json (output: ir_train_output.json, ir_dev_output.json)
3. Use TestDatasetGenerator.py to retrieve the sentences for ir_train_output.json and ir_dev_output.json (output: train_evidence.jsonl, dev_evidence.jsonl)
4. Train the model:

    allennlp train label_classifier.json --serialization-dir tmp/train_data --include-package NLP


For test:
1. Use QueryWikis.py to query evidences for test-unlabelled.json (output: ir_test-unlabelled.json)
2. Use TestDatasetGenerator.py to retrieve the sentences for ir_test-unlabelled.json (output: test_evidence.jsonl)
3. Predict:
    
    allennlp predict tmp/train_data/model.tar.gz test_evidence.jsonl --include-package NLP --predictor fact_predictor --output-file outputPredictions.json --use-dataset-reader
    
4. Use FinalResultPrinter.py to format the answer
