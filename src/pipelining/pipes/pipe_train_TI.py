from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4


class Config1(ConfigRoot):
    # g1 combined with tr2 produces gold data that was formerly persisted as 's1_articles__tr2_1__sc_sm_alle_anwendungsfelder.json'
    gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule5

class Config2(ConfigRoot):
    # formerly s3 in prodigy, now p2 in prodigy data, and persisted as gold data as g5
    gold_data_json_path = data_flow_registry.gold_data["g5"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule10

class Config3(ConfigRoot):
    # formerly s4 in prodigy, now p3 in prodigy data, and persisted as gold data as g6
    gold_data_json_path = data_flow_registry.gold_data["g6"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule10

class Config4(ConfigRoot):
    # formerly s5 in prodigy, now p4 in prodigy data, and persisted as gold data as g7
    gold_data_json_path = data_flow_registry.gold_data["g7"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule10

class Config5(ConfigRoot):
    # formerly s6 in prodigy, now p5 in prodigy data, and persisted as gold data as g8
    gold_data_json_path = data_flow_registry.gold_data["g8"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule10

class ConfigTrain(ConfigRoot):

    should_create_model = True
    should_persist_model = True
    model_def_dict = data_flow_registry.models["mo10"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]
    exclusive_classes = model_def_dict["exclusive_classes"]


def run():

    gdc_1 = main.load_gold_data(Config1)
    gdc_1 = main.transform_gold_data(Config1, gdc_1)
    gdc = GoldDataContainer(cats_list=gdc_1.cats_list)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_1)

    gdc_2 = main.load_gold_data(Config2)
    gdc_2 = main.transform_gold_data(Config2, gdc_2)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_2)

    gdc_3 = main.load_gold_data(Config3)
    gdc_3 = main.transform_gold_data(Config3, gdc_3)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_3)

    gdc_4 = main.load_gold_data(Config4)
    gdc_4 = main.transform_gold_data(Config4, gdc_4)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_4)

    gdc_5 = main.load_gold_data(Config5)
    gdc_5 = main.transform_gold_data(Config5, gdc_5)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_5)

    trainer = main.init_trainer(ConfigTrain, cats_list=gdc.cats_list)
    main.run_training(config=ConfigTrain, trainer=trainer, gold_data_container=gdc)

    embed()
