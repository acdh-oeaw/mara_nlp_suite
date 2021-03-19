from typing import List
import spacy
from datetime import datetime
import random
from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from trainer.abstract_trainer import AbstractTrainer
from loggers import log_manager


class Trainer4(AbstractTrainer):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)


    def create_model(self, cats, spacy_base_model):

        nlp = spacy.load(spacy_base_model, disable=["tagger", "parser", "ner"])

        if cats is not None:

            if self.exclusive_classes is not None:

                textcat = nlp.create_pipe("textcat", config={"exclusive_classes": self.exclusive_classes})

            else:

                textcat = nlp.create_pipe("textcat", config={"exclusive_classes": False})

            for cat in cats:

                textcat.add_label(cat)

            nlp.add_pipe(textcat, last=True)

        self.nlp = nlp
        self.cats = cats

        self.log_trainer("Created new spacy model")


    def load_model(self, model_path_to_load=None):

        if model_path_to_load is None:

            model_path_to_load = self.model_path

        nlp = spacy.blank("de")
        pipe = nlp.create_pipe("textcat")
        nlp.add_pipe(pipe)

        nlp.from_disk(model_path_to_load)

        self.nlp = nlp
        self.cats = list(self.get_textcat_pipeline().labels)

        self.log_trainer(f"Loaded model from path: {model_path_to_load}")


    def train(self, train_data: GoldDataContainer, eval_data: GoldDataContainer, iteration_limit: int):

        start = datetime.now()
        self.log_trainer(
            "--------------------------------"
            "\nSTART TRAINING\n"
        )

        self.log_trainer(f"model_path: {self.model_path}")
        self.log_trainer(f"train_data_json_path: {self.train_data_json_path}")
        self.log_trainer(f"should_create_model: {self.should_create_model}")
        self.log_trainer(f"should_load_model: {self.should_load_model}")
        self.log_trainer(f"should_persist_model: {self.should_persist_model}")
        self.log_trainer(f"cats: {self.cats}")
        self.log_trainer(f"spacy.prefer_gpu(): {spacy.prefer_gpu()}")
        self.log_trainer(f"iteration_limit: {iteration_limit}")
        self.log_trainer(f"len(train_data): {len(train_data.gold_data_item_list)}")
        self.log_trainer(f"len(eval_data): {len(eval_data.gold_data_item_list)}")

        # TODO : add hashing of assigned cats
        # TODO : Write cats_list to log too
        hash_texts_train_data = self.get_hash_of_texts([gdi.text for gdi in train_data.gold_data_item_list])
        self.log_trainer(f"hash of texts in train_data: {hash_texts_train_data}")
        hash_texts_eval_data = self.get_hash_of_texts([gdi.text for gdi in eval_data.gold_data_item_list])
        self.log_trainer(f"hash of texts in eval_data: {hash_texts_eval_data}")

        textcat = self.get_textcat_pipeline()
        self.log_trainer(f"textcat.cfg.get('exclusive_classes', None): {textcat.cfg.get('exclusive_classes', None)}")

        dropout = 0.2
        self.log_trainer(f"dropout: {dropout}")

        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe not in ["textcat", "trf_wordpiecer", "trf_tok2vec"]]
        with self.nlp.disable_pipes(*other_pipes):
            optimizer = self.nlp.begin_training()

            for iteration in range(1, iteration_limit+1):
                losses = {}

                start_iteration = datetime.now()
                self.log_trainer(f"Start iteration: {iteration}")


                for text, annotations in train_data.get_in_spacy_format():

                    self.nlp.update([text], [annotations], sgd=optimizer, drop=dropout, losses=losses)

                end_iteration = datetime.now()
                self.log_trainer(f"End iteration: {iteration}")
                self.log_trainer(f"duration iteration: {end_iteration - start_iteration}")

                self.log_trainer(f"losses: {losses['textcat']}")

                if len(eval_data.gold_data_item_list) > 0:

                    scores, _ = self.evaluate(eval_data)
                    self.log_trainer(f"overall score: {scores['textcat_score']}")
                    # https://github.com/explosion/spaCy/blob/26a90f011b8c21dfc06940579479aaff8006ff74/spacy/scorer.py#L164

                    for cat in scores['textcats_per_cat']:

                        self.log_trainer(f"scores for '{cat}': {scores['textcats_per_cat'][cat]}")

                if self.should_persist_model:

                    self.persist_model()

        end = datetime.now()
        self.log_trainer("END TRAINING")
        self.log_trainer(f"DURATION TRAINING: {end - start}")


    def evaluate(self, eval_data_container: GoldDataContainer):

        scores_spacy = self.evaluate_spacy(eval_data_container)

        scores_manual = self.evaluate_manually(eval_data_container)

        self.log_trainer(
            "--------------------------------\n"
            f"All evaluations complete.\n"
        )

        return scores_spacy, scores_manual


    def evaluate_spacy(self, eval_data_container: GoldDataContainer):

        assert self.get_textcat_pipeline().cfg['exclusive_classes'] is not None

        scorer = self.nlp.evaluate(
            eval_data_container.get_in_spacy_format(),
            verbose=False,
        )

        # scorer = spacy.scorer.Scorer(pipeline=self.nlp.pipeline)
        #
        # for ed in eval_data_container.gold_data_item_list:
        #
        #     doc_with_cats = self.nlp(ed.text) # tokenization + predictions
        #
        #     gold = spacy.gold.GoldParse(
        #         self.nlp.make_doc(ed.text), # tokenization only, no predictions
        #         cats=ed.cats # correct categories
        #     )
        #
        #     scorer.score(doc_with_cats, gold, verbose=True)

        self.log_trainer(
             "Spacy's scores: {\n" +
            f"  'textcat_score': {scorer.scores['textcat_score']}\n" +
             "  'textcats_per_cat': {\n" +
             ''.join([ f"    '{name}': {value}\n" for name, value in scorer.scores['textcats_per_cat'].items() ]) +
             "  }\n" +
             "}"
        )

        return scorer.scores

    def evaluate_manually(self, eval_data_container: GoldDataContainer):

        count = {}
        for label in self.cats:
            count[label] = {}
            count[label]['tp'] = 0  # True positives
            count[label]['fp'] = 1e-8  # False positives
            count[label]['fn'] = 1e-8  # False negatives
            count[label]['tn'] = 0  # True negatives

        for ed in eval_data_container.gold_data_item_list:

            doc = self.nlp(ed.text) # tokenization + predictions

            highest_prediction = max(doc.cats, key=doc.cats.get)  # get the label with the highest score

            for label, score in doc.cats.items():

                score_gold = ed.cats[label]  # get the correct value for this label

                # To evaluate exclusive categories
                if self.get_textcat_pipeline().cfg['exclusive_classes']:

                    # Only 1 label can be assigned, and we choose the one with the highest score
                    if label == highest_prediction and score_gold == 1.0:
                        count[label]['tp'] += 1
                    elif label == highest_prediction and score_gold == 0.0:
                        count[label]['fp'] += 1
                    elif label != highest_prediction and score_gold == 1.0:
                        count[label]['fn'] += 1
                    elif label != highest_prediction and score_gold == 0.0:
                        count[label]['tn'] += 1

                # To evaluate non-exclusive categories
                else:
                    # Any label that scores above 0.5 will be assigned
                    # TODO: Should this threshold be up for debate?

                    if score >= 0.5 and score_gold == 1.0:
                        count[label]['tp'] += 1.0
                    elif score >= 0.5 and score_gold == 0.0:
                        count[label]['fp'] += 1.0
                    elif score < 0.5 and score_gold == 1.0:
                        count[label]['fn'] += 1
                    elif score < 0.5 and score_gold == 0.0:
                        count[label]['tn'] += 1

        for label in self.cats:

            tp = count[label]['tp']
            fp = count[label]['fp']
            fn = count[label]['fn']

            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            if (precision + recall) == 0:
                f_score = 0.0
            else:
                f_score = 2 * (precision * recall) / (precision + recall)

            count[label]['precision'] = precision
            count[label]['recall'] = recall
            count[label]['f_score'] = f_score

        tp = sum([ count[label]['tp'] for label in self.cats ])
        fp = sum([ count[label]['fp'] for label in self.cats ])
        fn = sum([ count[label]['fn'] for label in self.cats ])
        precision = tp / (tp + fp)
        recall = tp / (tp + fn)
        f_value = 0.0 if (precision + recall) == 0 else 2 * (precision * recall) / (precision + recall)

        self.log_trainer(
             "Manual scores: {\n" +
            f"  'precision': {precision}\n" +
            f"  'recall': {recall}\n" +
            f"  'F1': {f_value}\n" +
             "  'individual scores': {\n" +
             ''.join([ f"    '{name}': {value}\n" for name, value in count.items() ]) +
             "  }\n" +
             "}\n"
        )
