from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4

class ConfigBase(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule7

    should_create_model = True
    should_persist_model = True


class ConfigTdc100(ConfigBase):

    model_def_dict = data_flow_registry.models["mo11"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]
    exclusive_classes = model_def_dict["exclusive_classes"]
    spacy_base_model = model_def_dict["spacy_base_model"]

class ConfigTdc80(ConfigBase):

    model_def_dict = data_flow_registry.models["mo12"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]
    exclusive_classes = model_def_dict["exclusive_classes"]
    spacy_base_model = model_def_dict["spacy_base_model"]


def run():

    gdc = main.load_gold_data(ConfigBase)
    gdc = main.transform_gold_data(ConfigBase, gdc)

    trainer = main.init_trainer(ConfigTdc100, cats_list=gdc.cats_list)
    main.run_training(config=ConfigTdc100, trainer=trainer, gold_data_container=gdc)

    trainer = main.init_trainer(ConfigTdc80, cats_list=gdc.cats_list)
    main.run_training(config=ConfigTdc80, trainer=trainer, gold_data_container=gdc)
