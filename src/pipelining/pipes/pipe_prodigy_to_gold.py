from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules
from pipelining import data_flow_registry
from IPython import embed
import main

class ConfigSub(ConfigRoot):

    prodigy_dataset_name = data_flow_registry.prodigy_data["p5"]["dataset_name"]
    gold_data_json_path = data_flow_registry.gold_data["g8"]["path"]

def run():

    gdc = main.load_prodigy_dataset(ConfigSub)
    main.persist_gold_data(ConfigSub, gdc)
