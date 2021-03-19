import importlib
import sys

import spacy
from IPython import embed
from typing import Type, List, Tuple
# from configs.config_template import ConfigTemplate # TODO
from pipelining.pipe_root import ConfigRoot
from indexer import reference_table_initiator
from trainer.abstract_trainer import AbstractTrainer
from etl import maxqdata_manager, gold_data_manager, db_manager
from etl.gold_data_manager import GoldDataContainer
from indexer import model_indexer, lmvr_indexer, ske_translator
from annotators import prodigy_manager
from loggers import log_manager
from etl.gold_data_transform_rules import TransformRule

# TODO : Save non-None config variables into log at start up
# TODO : add functions for calling json transformations and evaluations
# TODO : Consider to load the modules of indexer and prodigy_manager dynamically via configs
# TODO : Consider to enable these root functions to also accept single paramters besides whole config classes

def main(config: Type[ConfigRoot]):

    config, pipe = handle_cli_args(config)

    # TODO: It isn't ideal to init the log_manager here because we might want output during _update_config_with_cli_args
    # But I really wanted to get a custom log_global_path
    log_manager.initialize(config.log_global_path)
    log_manager.info_global(
        f"--------------------------------"
        f"\nSTART MAIN\n"
    )

    pipe.run()


def handle_cli_args(config: Type[ConfigRoot]) -> Type[ConfigRoot]:

    args = sys.argv
    cli_params = {}
    pipe = None

    for i, c in enumerate(args):

        # if c == "--config":
        if c == "--pipe":
            # replace the config module with another config

            # config_module = importlib.import_module(f"configs.{args[i + 1]}")
            # config = getattr(config_module, "ConfigSub")

            pipe = importlib.import_module(f"pipelining.pipes.{args[i + 1]}")

        # TODO: create possibility to load trainer via CLI string param

        elif c.startswith("--"):

            try:
                val = args[i + 1]
            except:
                raise Exception(f"No argument was passed to parameter: '{c}'")

            try:
                val = int(val)
            except:
                pass

            if val == "True":
                val = True
            elif val == "False":
                val = False

            cli_params[c[2:]] = val

    if pipe is None:
        raise Exception # TODO

    # load secret config file with credentials if it exists
    try:
        credentials = importlib.import_module(f"credentials")

        for key in dir(credentials):
            if not key.startswith('__'):
                setattr(config, key, getattr(credentials, key))

        #log_manager.debug_global("Loaded credential config")

    except ModuleNotFoundError:
        pass

    # update the config module with CLI arguments

    for k, v in cli_params.items():

        if not hasattr(config, k):
            raise Exception(f"Found invalid variable: {k}")

        setattr(config, k, v)

    return config, pipe


def load_from_maxqdata(config: Type[ConfigRoot]) -> GoldDataContainer:

    log_manager.info_global(
        "--------------------------------"
        "\nLoading and transforming data from AMC and maxqdata export file\n"
    )

    if config.should_do_dummy_run:
        limit_percent_data = 10
    else:
        limit_percent_data = 100

    root_coding_node, article_annotated_list = maxqdata_manager.load_from_amc_and_maxqdata(
        annotations_xlsx_file_path=config.annotations_xlsx_file_path,
        articles_xml_directory=config.articles_xml_directory,
        limit_percent_data=limit_percent_data
    )

    if config.maxqdata_gold_data_transform_function == maxqdata_manager.transform_to_gold_data_articles:

        return maxqdata_manager.transform_to_gold_data_articles(
            root_coding_node=root_coding_node,
            article_annotated_list=article_annotated_list
        )

    elif config.maxqdata_gold_data_transform_function == maxqdata_manager.transform_to_gold_data_sentences:

        nlp = spacy.load(config.spacy_base_model, disable=["tagger", "parser", "ner"])
        if "sentencizer" not in nlp.pipe_names:
            nlp.add_pipe(nlp.create_pipe("sentencizer"))
        sentence_split_func = lambda t : nlp(t).sents

        return maxqdata_manager.transform_to_gold_data_sentences(
            spacy_base_model=config.spacy_base_model,
            root_coding_node=root_coding_node,
            article_annotated_list=article_annotated_list,
            sentence_split_func=sentence_split_func
        )

    else:

        raise Exception("No maxqdata_gold_data_transform_function defined.")


def transform_gold_data(
    config: Type[ConfigRoot],
    gold_data_container: GoldDataContainer
):

    log_manager.info_global(
        "--------------------------------"
        "\nTransforming gold data\n"
    )

    return gold_data_manager.transform_cats(
        gold_data_transform_rule=config.gold_data_transform_rule,
        gold_data_container=gold_data_container
    )


def persist_gold_data(
    config: Type[ConfigRoot],
    gold_data_container: GoldDataContainer,
):

    log_manager.info_global(
        "--------------------------------"
        "\nPersisting transformed data into json structured for training\n"
    )

    if config.should_do_dummy_run:

        config.gold_data_json_path = config.gold_data_json_path.replace(".json", "__dummy.json")
        gold_data_container.gold_data_item_list = gold_data_container.gold_data_item_list[:40]

    gold_data_manager.persist_to_json(config.gold_data_json_path, gold_data_container)


def load_gold_data(config: Type[ConfigRoot]) -> GoldDataContainer:

    log_manager.info_global(
        "--------------------------------"
        "\nLoading gold data from json file\n"
    )

    return gold_data_manager.load_from_json(
        gold_data_json_path=config.gold_data_json_path
    )


def init_trainer(config: Type[ConfigRoot], cats_list: List[str] = None) -> AbstractTrainer:

    log_manager.info_global(
        "--------------------------------"
        "\nInitializing model\n"
    )

    model_path = config.model_path
    if config.should_do_dummy_run and config.should_persist_model:
        model_path +="__dummy"

    assert config.trainer_class is not None

    return config.trainer_class(
        spacy_base_model=config.spacy_base_model,
        model_path=model_path,
        should_persist_model=config.should_persist_model,
        should_load_model=config.should_load_model,
        should_create_model=config.should_create_model,
        cats=cats_list,
        gold_data_json_path=config.gold_data_json_path,
        exclusive_classes=config.exclusive_classes
    )


def run_training(config: Type[ConfigRoot], trainer: AbstractTrainer, gold_data_container: GoldDataContainer):

    log_manager.info_global(
        "--------------------------------"
        "\nTraining model\n"
    )

    train_data_container, eval_data_container = gold_data_manager.split_into_train_eval_data(
        gold_data_container=gold_data_container,
        data_cutoff=config.train_data_cutoff,
    )

    if config.should_do_dummy_run:

        train_data_container.gold_data_item_list = train_data_container.gold_data_item_list[:20]
        eval_data_container.gold_data_item_list = eval_data_container.gold_data_item_list[:20]
        config.iteration_limit = 2

    trainer.train(
        train_data=train_data_container,
        eval_data=eval_data_container,
        iteration_limit=config.iteration_limit
    )

    return train_data_container, eval_data_container


def run_prodigy(config: Type[ConfigRoot]):

    log_manager.info_global(
        "--------------------------------"
        "\nRunning prodigy\n"
    )

    if config.should_do_dummy_run:

        config.db_host = "127.0.0.1"
        config.db_name = "mara_db_dummy"
        config.db_user = "mara_user_dummy"
        config.db_password = "mara_password_dummy"
        config.db_port = 5432
        config.ske_batch_size = 2

    prodigy_manager.run(
        ske_config={
            "ske_rest_url": config.ske_rest_url,
            "ske_corpus_id": config.ske_corpus_id,
            "ske_user": config.ske_user,
            "ske_password": config.ske_password,
        },
        db_config={
            "host": config.db_host,
            "dbname": config.db_name,
            "user": config.db_user,
            "password": config.db_password,
            "port": config.db_port
        },
        dataset_name=config.prodigy_dataset_name,
        index1_table_name=config.index_table_name,
        index2_table_names=config.index_lmvr_table_names,
        ske_translation_table_name=config.ske_docid_url_table_name
    )


def run_model_indexer(config: Type[ConfigRoot], trainer):

    log_manager.info_global(
        "--------------------------------"
        "\nRunning indexer\n"
    )

    ske_config = {
        "ske_rest_url": config.ske_rest_url,
        "ske_corpus_id": config.ske_corpus_id,
        "ske_user": config.ske_user,
        "ske_password": config.ske_password,
    }
    db_config = {
        "host": config.db_host,
        "dbname": config.db_name,
        "user": config.db_user,
        "password": config.db_password,
        "port": config.db_port
    }

    if config.indexing_function == model_indexer.index_articles:

        model_indexer.index_articles(
            ske_config=ske_config,
            db_config=db_config,
            index_table_name=config.index_table_name,
            trainer=trainer,
            table_name_ref_articles=config.table_name_ref_articles,
            should_do_dummy_run=config.should_do_dummy_run,
        )

    elif config.indexing_function == model_indexer.index_sentences:

        model_indexer.index_sentences(
            ske_config=ske_config,
            db_config=db_config,
            index_table_name=config.index_table_name,
            trainer=trainer,
            table_name_ref_articles=config.table_name_ref_articles,
            should_do_dummy_run=config.should_do_dummy_run,
        )


def run_ske_translator(config: Type[ConfigRoot]):

    log_manager.info_global(
        "--------------------------------"
        "\nRunning SKE translator\n"
    )

    ske_translator.run(
        ske_config={
            "ske_rest_url": config.ske_rest_url,
            "ske_corpus_id": config.ske_corpus_id,
            "ske_user": config.ske_user,
            "ske_password": config.ske_password
        },
        db_config={
            "host": config.db_host,
            "dbname": config.db_name,
            "user": config.db_user,
            "password": config.db_password,
            "port": config.db_port
        },
        docid_table_name=config.ske_docid_url_table_name,
        index1_table_name=config.index_table_name,
        index2_table_names=config.index_lmvr_table_names,
        should_drop_create_table=config.should_drop_create_ske_translator_table
    )


def run_lvmr_indexer(config: Type[ConfigRoot]):

    log_manager.info_global(
        "--------------------------------"
        "\nRunning LMVR indexer\n"
    )

    lmvr_indexer.run(
        data_path=config.csv_folder_path,
        db_config={
            "host": config.db_host,
            "dbname": config.db_name,
            "user": config.db_user,
            "password": config.db_password,
            "port": config.db_port
        },
        index1_table_name=config.index_table_name,
        index2_table_names=config.index_lmvr_table_names,
        ske_config={
            "ske_rest_url": config.ske_rest_url,
            "ske_corpus_id": config.ske_corpus_id,
            "ske_user": config.ske_user,
            "ske_password": config.ske_password
        }
    )


def load_prodigy_dataset(config: Type[ConfigRoot]):

    log_manager.info_global(
        "--------------------------------"
        "\nLoading prodigy data\n"
    )

    prodigy_data = db_manager.get_prodigy_data(
        dataset_name=config.prodigy_dataset_name,
        db_config={
            "host": config.db_host,
            "dbname": config.db_name,
            "user": config.db_user,
            "password": config.db_password,
            "port": config.db_port
        },
        ske_config={
            "ske_rest_url": config.ske_rest_url,
            "ske_corpus_id": config.ske_corpus_id,
            "ske_user": config.ske_user,
            "ske_password": config.ske_password
        })

    return prodigy_data

def init_reference_tables(config: Type[ConfigRoot]):
    """Creates the main index table where all articles of a sketch engine corpus are loaded
    and their pos_ids and urls are persisted. Should be only done once per sub corpus.
    Other indices will refer to this main index as foreign keys."""

    log_manager.info_global(
        "--------------------------------"
        "\nCreating main reference table for indexing\n"
    )

    reference_table_initiator.init(
        db_config={
            "host": config.db_host,
            "dbname": config.db_name,
            "user": config.db_user,
            "password": config.db_password,
            "port": config.db_port
        },
        ske_config={
            "ske_rest_url": config.ske_rest_url,
            "ske_corpus_id": config.ske_corpus_id,
            "ske_user": config.ske_user,
            "ske_password": config.ske_password
        },
        table_name_ref_articles=config.table_name_ref_articles,
        table_name_ref_sentences=config.table_name_ref_sentences,
        spacy_base_model=config.spacy_base_model,
        should_do_dummy_run=config.should_do_dummy_run,
    )


def run_evaluation(config: Type[ConfigRoot], model: AbstractTrainer):

    # We assume that the model and the eval_data have the same categories
    # If not, this should be fixed in the eval_data by providing TransformRules

    # for eval_task in config.evaluation_tasks:
    #
    #     eval_data_container = load_gold_data_OLD(eval_task, config)
    #
    #     # TODO: for exclusive classes, make sure the eval data don't contain items where more than 1 category is selected
    #
    #     # TODO: assert the categories in eval_data_container matche the categories in the model
    #
    #     # TODO: add an option to compare the eval_data_container's hash value to the one stored in the model for the portion of data it didn't train on
    #
    #     scores_spacy, scores_manual = model.evaluate(eval_data_container)

    # TODO sabine: confirm if my changes are equivalent to the logic from before
    eval_data_container = load_gold_data(config)
    eval_data_container = transform_gold_data(config, eval_data_container) # TODO: It should be possible to perform multiple transformations
    scores_spacy, scores_manual = model.evaluate(eval_data_container)


if __name__ == "__main__":

    try:
        main(ConfigRoot)
    except Exception as ex:
        log_manager.exception_global(ex)