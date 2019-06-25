"""
Created on Tue May 21 20:57:31 2019

This class is useless as we use --use-dataset-reader to predict, but the command still need a predictor as a parameter
"""


from overrides import overrides
from allennlp.common.util import JsonDict
from allennlp.data import Instance
from allennlp.predictors.predictor import Predictor

@Predictor.register("fact_predictor")
class FactPredictor(Predictor):
    
    def predict(self, premise: str, hypothesis: str) -> JsonDict:
        return self.predict_json({"premise" : premise, "hypothesis": hypothesis})
    
    @overrides
    def _json_to_instance(self, json_dict: JsonDict) -> Instance:
        evidence = json_dict["evidence"]
        claim = json_dict["claim"]
        return self._dataset_reader.text_to_instance(evidence = evidence, claim = claim)
    