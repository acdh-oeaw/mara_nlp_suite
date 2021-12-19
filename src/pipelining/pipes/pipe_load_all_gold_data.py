from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main


class ConfigRead1(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]

class ConfigRead2(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g2"]["path"]

class ConfigRead3(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g3"]["path"]

class ConfigRead4(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g4"]["path"]

class ConfigRead5(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g5"]["path"]

class ConfigRead6(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g6"]["path"]

class ConfigRead7(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g7"]["path"]

class ConfigRead8(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g8"]["path"]

class ConfigRead9(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g9"]["path"]

class ConfigRead10(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g10"]["path"]



def run():

    gdc_1 = main.load_gold_data(ConfigRead1)
    gdc_2 = main.load_gold_data(ConfigRead2)
    gdc_3 = main.load_gold_data(ConfigRead3)
    gdc_4 = main.load_gold_data(ConfigRead4)
    gdc_5 = main.load_gold_data(ConfigRead5)
    gdc_6 = main.load_gold_data(ConfigRead6)
    gdc_7 = main.load_gold_data(ConfigRead7)
    gdc_8 = main.load_gold_data(ConfigRead8)
    gdc_9 = main.load_gold_data(ConfigRead9)
    gdc_10 = main.load_gold_data(ConfigRead10)
