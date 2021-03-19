from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules
from pipelining import data_flow_registry
from IPython import embed
import main


class ConfigIndex(ConfigRoot):

    model_path = data_flow_registry.models["mo9"]["path"]

    index_table_name = "i_TEST"
    indexing_function = data_flow_registry.model_indices["i1"]["index_creation_logic"]


def run():

    from trainer.trainer4 import Trainer4
    ConfigRoot.trainer_class = Trainer4
    ConfigRoot.should_load_model = True

    ConfigRoot.table_name_ref_articles = "main_ref_articles"

    trainer = main.init_trainer(ConfigIndex)
    main.run_model_indexer(ConfigIndex, trainer)

