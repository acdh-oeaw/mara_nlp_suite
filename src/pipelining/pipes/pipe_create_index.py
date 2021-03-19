from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules
from pipelining import data_flow_registry
from IPython import embed
import main


class ConfigIndex(ConfigRoot):

    # index
    index_def = data_flow_registry.model_indices["i6"]
    index_table_name = index_def["table_name"]
    indexing_function = index_def["index_creation_logic"]

    # model
    model_key = index_def["source"][1]
    model_path = data_flow_registry.models[model_key]["path"]
    from trainer.trainer4 import Trainer4
    trainer_class = Trainer4
    should_load_model = True


def run():

    trainer = main.init_trainer(ConfigIndex)
    main.run_model_indexer(ConfigIndex, trainer)
