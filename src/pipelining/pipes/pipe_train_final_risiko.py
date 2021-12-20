from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main


class ConfigLoad1(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule11

class ConfigLoad2(ConfigRoot):

    gold_data_transform_rule = gold_data_transform_rules.TransformRule18


class ConfigTrain(ConfigRoot):

    should_create_model = True
    should_persist_model = True
    model_def_dict = data_flow_registry.models["mo17"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]
    exclusive_classes = model_def_dict["exclusive_classes"]


def run():

    gdc_original = main.load_gold_data(ConfigLoad1)
    gdc_detailed = main.transform_gold_data(ConfigLoad1, gdc_original)
    gdc_grouped = main.transform_gold_data(ConfigLoad2, gdc_detailed.copy())

    gdc_merged = GoldDataContainer()
    gdc_merged.cats_list = gdc_grouped.cats_list + gdc_detailed.cats_list
    gdc_merged.gold_data_item_list = []
    for gdi_detailed, gdi_grouped in zip(gdc_detailed.gold_data_item_list, gdc_grouped.gold_data_item_list):
        if gdi_detailed.article_id != gdi_grouped.article_id or gdi_detailed.text != gdi_grouped.text:
            raise Exception()
        else:
            cats_merged = {}
            cats_merged.update(gdi_detailed.cats)
            cats_merged.update(gdi_grouped.cats)

            gdc_merged.gold_data_item_list.append(
                GoldDataItem(
                    article_id=gdi_detailed.article_id,
                    text=gdi_detailed.text,
                    cats=cats_merged
                )
            )


    trainer = main.init_trainer(ConfigTrain, cats_list=gdc_merged.cats_list)
    main.run_training(ConfigTrain, trainer, gdc_merged)
