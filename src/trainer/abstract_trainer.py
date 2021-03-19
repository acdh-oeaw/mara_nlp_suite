import zlib
import random
from typing import List
from spacy.language import Language
from loggers import log_manager


class AbstractTrainer:

    model_path: str
    spacy_base_model: str
    gold_data_json_path: str
    cats: List[str]
    should_load_model: bool
    should_create_model: bool
    should_persist_model: bool
    exclusive_classes: bool
    nlp: Language

    def __init__(
        self,
        model_path=None,
        spacy_base_model=None,
        should_load_model=None,
        should_create_model=None,
        should_persist_model=None,
        cats=None,
        gold_data_json_path=None,
        exclusive_classes=None
    ):

        if model_path is not None:
            if model_path[-1] != "/":
                model_path += "/"

            # TODO: when the same model is instantiated multiple times, this logger is instantiated multiple times too
            # TODO: change logger so that when should_persist_model==False, the logger only uses the global logger
            self.logger = log_manager.create_new_logger(model_path + "log.txt")

        else:
            self.logger = None # TODO: Use global log_manager instead

        log_manager.info_global(f"Instantiating Trainer Object")

        self.model_path = model_path
        self.train_data_json_path = gold_data_json_path
        self.exclusive_classes = exclusive_classes
        self.should_create_model = should_create_model
        self.should_load_model = should_load_model
        self.should_persist_model = should_persist_model
        self.nlp = None

        if should_create_model and not should_load_model:

            self.create_model(cats=cats, spacy_base_model=spacy_base_model)

        elif not should_create_model and should_load_model:

            self.load_model()

        else:

            raise Exception("Ambiguity between should_load_model and should_create_model.")


    def create_model(self, **kwargs):

        pass


    def load_model(self, **kwargs):

        pass


    def train(self, **kwargs):

        pass


    def evaluate(self, **kwargs):

        pass


    def persist_model(self, model_path_to_persist=None):

        if model_path_to_persist is None:

            model_path_to_persist = self.model_path

        self.nlp.to_disk(model_path_to_persist)
        self.log_trainer(f"persisted to path: {model_path_to_persist}")


    def get_textcat_pipeline(self):

        if "textcat" not in self.nlp.pipe_names and self.cats is None:

            raise Exception(
                "spacy Pipeline 'textcat' was not added. "
                "This is likely due to the fact that cats were not assigned to this trainer "
                "when it was created."
            )

        return self.nlp.get_pipe("textcat")


    def predict(self, text):

        return self.nlp(text).cats


    def predict_and_sort(self, text):

        cats_predicted = self.predict(text)
        cats_predicted = sorted(cats_predicted.items(), key=lambda item: item[1])
        return cats_predicted


    def predict_and_compare(self, text, cats_gold):

        cats_predicted_sorted = self.predict_and_sort(text)
        cats_compared = []

        for cat_pred in cats_predicted_sorted:

            cats_compared.append({
                "cat": cat_pred[0],
                "predicted": cat_pred[1],
                "gold": cats_gold[cat_pred[0]]
            })

        return cats_compared


    def predict_and_compare_random(self, data_list):

        rand_index = random.randint(0, len(data_list)-1)

        data_tuple = data_list[rand_index]

        return (
            [{"rand_index": rand_index}]
            + self.predict_and_compare(text=data_tuple[0], cats_gold=data_tuple[1]["cats"])
        )


    def split_text_into_sentences(self):
        # Work in progress
        pass



    def get_hash_of_texts(self, texts):

        # Default hashing in python is changed due to different seeding or something at runtime
        # the following ensures that the same texts produce the same hashes over several runtime executions
        text_hashes = [zlib.adler32(str.encode(t)) for t in texts]
        text_hashes_byte = str(sum(text_hashes)).encode()

        return zlib.adler32(text_hashes_byte)


    def log_trainer(self, msg):

        self.logger.info(msg)
        log_manager.info_global(msg)