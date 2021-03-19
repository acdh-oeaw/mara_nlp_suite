from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4


# TODO: This pipe is only half-way done by replicating parts of config_evaluate_AF.py

class ConfigSub(ConfigRoot):

    gold_data_json_path = None # TODO

    should_load_model = True
    model_def_dict = data_flow_registry.models[None] # TODO
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["model_path"]


def run():

    trainer = main.init_trainer(ConfigSub)
    main.run_evaluation(ConfigSub, trainer)

    embed()
