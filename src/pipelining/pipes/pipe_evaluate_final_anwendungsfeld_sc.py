from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
from pipelining.pipes import pipe_train_AF
from evaluators import evaluator
import main


class TrainDataConfig(ConfigRoot):

    gold_data_transform_rule = gold_data_transform_rules.TransformRule22


class EvalConfig(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g9"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule23
    evaluation_scores_path = data_flow_registry.evaluations_scores["es7"]["path"]
    evaluation_diffs_path = data_flow_registry.evaluation_diffs["ed7"]["path"]


class TrainConfig(ConfigRoot):

    should_load_model = True
    model_def_dict = data_flow_registry.models["mo9"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]


def run():

    trainer = main.init_trainer(TrainConfig)

    gdc_train = pipe_train_AF.load_and_transform_data()
    gdc_train = main.transform_gold_data(TrainDataConfig, gdc_train)
    gdc_eval_not = main.load_gold_data(EvalConfig)
    gdc_eval_not = main.transform_gold_data(EvalConfig, gdc_eval_not)

    af_sc = "AF: Social Companions"
    af_sc_not = "AF: NOT Social Companions"
    gdc_eval = GoldDataContainer(cats_list=[af_sc], gold_data_item_list=[])
    for gdi_not in gdc_eval_not.gold_data_item_list:
        gdi = GoldDataItem(article_id=gdi_not.article_id, text=gdi_not.text)
        if gdi_not.cats[af_sc_not] == 1:
            gdi.cats = {af_sc: 0}
        elif gdi_not.cats[af_sc_not] == 0:
            gdi.cats = {af_sc: 1}
        else:
            raise Exception
        gdc_eval.gold_data_item_list.append(gdi)

    evaluator.calc_and_write_all_tables(
        gdc_train=gdc_train,
        gdc_eval=gdc_eval,
        trainer=trainer,
        table_path_score=EvalConfig.evaluation_scores_path,
        table_path_diff=EvalConfig.evaluation_diffs_path,
        cats_are_exclusive=False
    )