"""
Created on Tue May 21 13:17:00 2019

Use to read data
"""

import json
from typing import Dict
from allennlp.data import Instance
from allennlp.data.fields import Field, TextField, LabelField, MetadataField
from allennlp.data.token_indexers import TokenIndexer, SingleIdTokenIndexer
from allennlp.data.tokenizers import Tokenizer, WordTokenizer
from allennlp.data.dataset_readers import DatasetReader

@DatasetReader.register("claim_evidence_reader")
class EvidenceDatasetReader(DatasetReader):
    def __init__(self, tokenizer: Tokenizer = None, token_indexers: Dict[str, TokenIndexer] = None) -> None:
        super().__init__(lazy = False)
        self._tokenizer = tokenizer or WordTokenizer()
        self._token_indexers = token_indexers or {"tokens": SingleIdTokenIndexer()}
    
    def text_to_instance(self, evidence:str, claim:str, label: str = None) -> Instance:
        fields: Dict[str, Field] = {}
        claim_tokens = self._tokenizer.tokenize(claim)
        evidence_tokens = self._tokenizer.tokenize(evidence)
        fields['premise'] = TextField(evidence_tokens, self._token_indexers)
        fields['hypothesis'] = TextField(claim_tokens, self._token_indexers)
        if label:
            fields['label'] = LabelField(label)
        metadata = {"premise_tokens": [x.text for x in evidence_tokens],
                    "hypothesis_tokens": [x.text for x in claim_tokens]}
        fields["metadata"] = MetadataField(metadata)
        return Instance(fields)
    
    def _read(self, file_path):
        with open(file_path) as train_json:
            for line in train_json:
                data = json.loads(line)
                claim = data["claim"]
                evidence = data["evidence"]
                label = None
                if "label" in data:
                    label = data["label"]
                yield self.text_to_instance(evidence, claim, label)
