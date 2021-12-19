from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main


class TransformConfigSC(ConfigRoot):

    articles_xml_directory = data_flow_registry.maxqdata_data["md3"]["articles_xml_directory"]
    annotations_xlsx_file_path = data_flow_registry.maxqdata_data["md3"]["annotations_xlsx_file_path"]
    maxqdata_gold_data_transform_function = data_flow_registry.gold_data["g9"]["maxqdata_specific_processing"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule15
    gold_data_json_path = data_flow_registry.gold_data["g9"]["path"]


class TransformConfigSM(ConfigRoot):

    articles_xml_directory = data_flow_registry.maxqdata_data["md4"]["articles_xml_directory"]
    annotations_xlsx_file_path = data_flow_registry.maxqdata_data["md4"]["annotations_xlsx_file_path"]
    maxqdata_gold_data_transform_function = data_flow_registry.gold_data["g10"]["maxqdata_specific_processing"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule16
    gold_data_json_path = data_flow_registry.gold_data["g10"]["path"]


def run():

    gdc_sc = main.load_from_maxqdata(TransformConfigSC)
    gdc_sc = main.transform_gold_data(TransformConfigSC, gdc_sc)
    main.persist_gold_data(TransformConfigSC, gdc_sc)

    gdc_sm = main.load_from_maxqdata(TransformConfigSM)
    gdc_sm = main.transform_gold_data(TransformConfigSM, gdc_sm)
    main.persist_gold_data(TransformConfigSM, gdc_sm)
