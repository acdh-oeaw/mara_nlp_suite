from typing import Type
from trainer.abstract_trainer import AbstractTrainer
from pipelining import data_flow_registry


class ConfigRoot:
    # TODO __sresch__ : Go through this and remove unused should_*
    # TODO: inspect for unused setting variables, and remove them

    data_flow_registry = data_flow_registry

    # -------------------------------------------------------
    # sketchengine settings

    ske_rest_url = None # hard-coding possible, but better pass this as CLI param!
    ske_corpus_id = None # hard-coding possible, but better pass this as CLI param!
    ske_user = None # hard-coding possible, but better pass this as CLI param!
    ske_password = None # hard-coding possible, but better pass this as CLI param!


    # -------------------------------------------------------
    # db settings

    db_host = None # hard-coding possible, but better pass this as CLI param!
    db_name = None # hard-coding possible, but better pass this as CLI param!
    db_user = None # hard-coding possible, but better pass this as CLI param!
    db_password = None # hard-coding possible, but better pass this as CLI param!
    db_port = None # hard-coding possible, but better pass this as CLI param!


    # -------------------------------------------------------
    # Everything related to ETL

    # articles as xml files exported from AMC
    articles_xml_directory = None

    # annotations done by human annotators exported as xlsx file from maxqdata
    annotations_xlsx_file_path = None

    #
    maxqdata_gold_data_transform_function = None

    #
    gold_data_transform_rule = None

    # The main training data json file
    gold_data_json_path = None

    # TODO : Inspect if these modules are necessary
    # The module name and class name of the trainer
    # If not specified, Trainer4 will be used
    model_module = None # e.g. "trainer.trainer4"
    model_class = None  # e.g. "Trainer4"

    # log main file
    log_global_path = "./log.txt"


    # -------------------------------------------------------
    # training configuration

    # The spacy base model upon which all other models will be built
    spacy_base_model = "de_core_news_sm"

    # The path of the model that should be loaded and/or persisted into
    model_path = None

    # In case several trainers are needed this list of model directories should be used
    model_path_list = None

    # Which class should be instantiated?
    trainer_class: Type[AbstractTrainer] = None

    # at which percentage point should the whole data set be split into training and evaluation data?
    train_data_cutoff = None

    # How many iterations should the training process go through?
    iteration_limit = None

    # Should the categories be handels as mutually exclusive?
    exclusive_classes = None


    # -------------------------------------------------------
    # indexing configuration

    indexer_class = None

    # TODO: Change this once the indexer persists into DB
    temporary_index_csv_file_path = None

    #
    should_init_index_ref_tables = None

    #
    table_name_ref_articles = "main_ref_articles"

    #
    table_name_ref_sentences = None


    # -------------------------------------------------------
    # annotators configuration

    # number of articles which should be evaluated by the classifier and from which one will be returned to the annotator
    ske_batch_size = None

    # deprecated, use `should_load_data` instead
    prodigy_dataset_name = None

    #
    indexing_function = None

    # The index table to be used in the pre-selection step in prodigy's stream
    index_table_name = None

    #
    index_lmvr_table_names = None

    #
    ske_docid_url_table_name = None

    # The path to the folder with the CSV files containing LMVR information
    csv_folder_path = None

    # -------------------------------------------------------
    # main logic decision flow

    should_load_data = None
    data_to_load = [
        {
            'source': 'you can write "json" or "prodigy"',
            'json_path': 'put a path here if your "source" is "json"',
            'dataset_name': 'put a dataset name here if your "source" is "prodigy"',
            'transformations': ['this is a list of class names of transformation rules']
        }
    ]

    # Should the data exported from AMC and maxqdata be transformed and loaded?
    # TODO: integrate this into `should_load_data`
    should_load_from_amc_and_maxqdata = None

    # This is deprecated for loading gold data, but it is still used to persist gold data
    should_transform_gold_data = None

    # Should the data from AMC and maxqdata which was loaded be persisted as json structured for training?
    should_persist_gold_data = None

    # deprecated, use `should_load_data` instead
    should_load_gold_data = None

    # Should do a dummy run? (Minimises data intensity for testing)
    should_do_dummy_run = None

    # Should a new model be created?
    should_create_model = None

    # Should an already trained model be loaded? (From model_path)
    should_load_model = None

    # Should training be done? (Needs should_load_training_data)
    should_run_training = None

    # Should the model be persisted? (To model_path)
    should_persist_model = None

    # Should annotators be launched? (Needs should_load_training_data, should_load_model)
    should_run_prodigy = None

    # Should an indexer be run?
    should_run_indexer = None

    #
    should_run_ske_translator = None

    #
    should_drop_create_ske_translator_table = None

    #
    should_run_lmvr_indexer = None

    # deprecated, use `should_load_data` instead
    should_load_prodigy_dataset = None

    # Launches an ipython shell after executing other functions. (In an IDE like pycharm it might be better to use the IDE's console however)
    should_run_in_shell = None

    # -------------------------------------------------------
    # Evaluation configs

    #
    evaluation_scores_path = None

    #
    evaluation_diffs_path = None

    should_run_evaluation = None
    evaluation_tasks = None
    # evaluation_tasks = [
    #     # Provide multiple tasks to compare evaluations
    #     # e.g.: evaluate dataset A, then evaluate dataset B, then evaluate dataset A+B
    #
    #     # Each evaluation task is a list of datasets and transformation rules
    #     # For example the following will yield 1 evaluation performed on the union of two data sets:
    #     [
    #         {
    #             "source": "prodigy",
    #             "dataset_name": "s99",
    #             "transformations": [TranformRule99, TransformRule98]
    #         },
    #         {
    #             "source": "json",
    #             "json_path": "../data/invalid_path.json",
    #             "transformations": []
    #         }
    #     ],
    # ]

    should_persist_eval_data = None


def run():
    raise Exception #TODO