from pipelining.pipe_root import ConfigRoot
from etl import gold_data_transform_rules
from pipelining import data_flow_registry
from IPython import embed
import main

class ConfigSub(ConfigRoot):

    model_def_dict = data_flow_registry.models["mo7"]
    spacy_base_model = model_def_dict["spacy_base_model"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]

    gold_data_json_path = data_flow_registry.gold_data[model_def_dict["source"][1]]["path"]
    gold_data_transform_rule = model_def_dict["gold_data_transform_rule"]

    should_create_model = True
    should_persist_model = True


def run():

    gdc = main.load_gold_data(ConfigSub)
    gdc = main.transform_gold_data(ConfigSub, gdc)
    trainer = main.init_trainer(config=ConfigSub, cats_list=gdc.cats_list)
    main.run_training(ConfigSub, trainer, gdc)
