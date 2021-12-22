from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
from pipelining.pipes import pipe_train_final_risiko
from evaluators import evaluator
import main


class EvalConfigSCDetailed(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g9"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule11

class EvalConfigSCGrouped(ConfigRoot):

    gold_data_transform_rule = gold_data_transform_rules.TransformRule18

class EvalConfigSCMerged(ConfigRoot):

    evaluation_scores_path = data_flow_registry.evaluations_scores["es5"]["path"]
    evaluation_diffs_path = data_flow_registry.evaluation_diffs["ed5"]["path"]

class EvalConfigSMDetailed(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g10"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule11

class EvalConfigSMGrouped(ConfigRoot):

    gold_data_transform_rule = gold_data_transform_rules.TransformRule18

class EvalConfigSMMerged(ConfigRoot):

    evaluation_scores_path = data_flow_registry.evaluations_scores["es6"]["path"]
    evaluation_diffs_path = data_flow_registry.evaluation_diffs["ed6"]["path"]


class TrainConfig(ConfigRoot):

    should_load_model = True
    model_def_dict = data_flow_registry.models["mo17"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]


def run():

    trainer = main.init_trainer(TrainConfig)

    gdc_train = pipe_train_final_risiko.load_and_transform_data()
    gdc_eval_sc_detailed = main.load_gold_data(EvalConfigSCDetailed)
    gdc_eval_sc_detailed = main.transform_gold_data(EvalConfigSCDetailed, gdc_eval_sc_detailed)
    gdc_eval_sc_grouped = main.transform_gold_data(EvalConfigSCGrouped, gdc_eval_sc_detailed.copy())
    gdc_eval_sc = gold_data_manager.extend_with_additional_cats(gdc_eval_sc_grouped, gdc_eval_sc_detailed)
    gdc_train, gdc_eval_sc = gold_data_manager.reduce_to_overlap(gdc_train, gdc_eval_sc)

    evaluator.calc_and_write_all_tables(
        gdc_train=gdc_train,
        gdc_eval=gdc_eval_sc,
        trainer=trainer,
        table_path_score=EvalConfigSCMerged.evaluation_scores_path,
        table_path_diff=EvalConfigSCMerged.evaluation_diffs_path,
        cats_are_exclusive=False
    )

    # Reloading train_data because in evaluating before it could have been modified for correspondence with evaluation data
    gdc_train = pipe_train_final_risiko.load_and_transform_data()
    gdc_eval_sm_detailed = main.load_gold_data(EvalConfigSMDetailed)
    gdc_eval_sm_detailed = main.transform_gold_data(EvalConfigSMDetailed, gdc_eval_sm_detailed)
    gdc_eval_sm_grouped = main.transform_gold_data(EvalConfigSMGrouped, gdc_eval_sm_detailed.copy())
    gdc_eval_sm = gold_data_manager.extend_with_additional_cats(gdc_eval_sm_grouped, gdc_eval_sm_detailed)
    gdc_train, gdc_eval_sm = gold_data_manager.reduce_to_overlap(gdc_train, gdc_eval_sm)

    # if  gdc_eval_sc.cats_list != gdc_eval_sm.cats_list != gdc_train.cats_list != trainer.cats:
    #     raise Exception

    evaluator.calc_and_write_all_tables(
        gdc_train=gdc_train,
        gdc_eval=gdc_eval_sm,
        trainer=trainer,
        table_path_score=EvalConfigSMMerged.evaluation_scores_path,
        table_path_diff=EvalConfigSMMerged.evaluation_diffs_path,
        cats_are_exclusive=False
    )