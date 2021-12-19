from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4


class ConfigReadGold(ConfigRoot):

    pass


class ConfigTrain(ConfigRoot):

    should_create_model = True
    should_persist_model = True
    model_def_dict = data_flow_registry.models["mo15"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]
    exclusive_classes = model_def_dict["exclusive_classes"]


def run():

    ConfigReadGold.gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
    ConfigReadGold.gold_data_transform_rule = gold_data_transform_rules.TransformRule3
    gdc_1 = main.load_gold_data(ConfigReadGold)
    gdc_1 = main.transform_gold_data(ConfigReadGold, gdc_1)

    ConfigReadGold.gold_data_transform_rule = gold_data_transform_rules.TransformRule13

    ConfigReadGold.gold_data_json_path = data_flow_registry.gold_data["g5"]["path"]
    gdc_5 = main.load_gold_data(ConfigReadGold)
    gdc_5 = main.transform_gold_data(ConfigReadGold, gdc_5)

    ConfigReadGold.gold_data_json_path = data_flow_registry.gold_data["g6"]["path"]
    gdc_6 = main.load_gold_data(ConfigReadGold)
    gdc_6 = main.transform_gold_data(ConfigReadGold, gdc_6)

    ConfigReadGold.gold_data_json_path = data_flow_registry.gold_data["g7"]["path"]
    gdc_7 = main.load_gold_data(ConfigReadGold)
    gdc_7 = main.transform_gold_data(ConfigReadGold, gdc_7)

    ConfigReadGold.gold_data_json_path = data_flow_registry.gold_data["g8"]["path"]
    gdc_8 = main.load_gold_data(ConfigReadGold)
    gdc_8 = main.transform_gold_data(ConfigReadGold, gdc_8)

    gdc = gold_data_manager.merge_assuming_identical_categories(gdc_1, gdc_5)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_6)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_7)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_8)

    # There are texts without Tonalität assigned, find and remove them:
    indices_to_remove = []
    for i, gdi in enumerate(gdc.gold_data_item_list):
        found = False
        for val in gdi.cats.values():
            if val == 1:
                found = True
        if not found:
            indices_to_remove.append(i)
    for i in indices_to_remove[-1::-1]:
        del gdc.gold_data_item_list[i]


    trainer = main.init_trainer(ConfigTrain, cats_list=gdc.cats_list)
    main.run_training(ConfigTrain, trainer, gdc)
