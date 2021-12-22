from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from pipelining.pipes import pipe_train_final_tonaliaet
from evaluators import evaluator
from IPython import embed
import main


class EvalConfigSC(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g9"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule3
    evaluation_scores_path = data_flow_registry.evaluations_scores["es1"]["path"]
    evaluation_diffs_path = data_flow_registry.evaluation_diffs["ed1"]["path"]


class EvalConfigSM(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g10"]["path"]
    gold_data_transform_rule = gold_data_transform_rules.TransformRule3
    evaluation_scores_path = data_flow_registry.evaluations_scores["es2"]["path"]
    evaluation_diffs_path = data_flow_registry.evaluation_diffs["ed2"]["path"]


class TrainerConfig(ConfigRoot):

    should_load_model = True
    model_def_dict = data_flow_registry.models["mo15"]
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = model_def_dict["iteration_limit"]
    exclusive_classes = model_def_dict["exclusive_classes"]


def run():

    gdc_train = pipe_train_final_tonaliaet.load_and_transform_data()

    gdc_eval_sc = main.load_gold_data(EvalConfigSC)
    gdc_eval_sc = main.transform_gold_data(EvalConfigSC, gdc_eval_sc)
    gdc_eval_sc = gdc_eval_sc.remove_cats_without_assignments()

    gdc_eval_sm = main.load_gold_data(EvalConfigSM)
    gdc_eval_sm = main.transform_gold_data(EvalConfigSM, gdc_eval_sm)
    gdc_eval_sm = gdc_eval_sm.remove_cats_without_assignments()

    trainer = main.init_trainer(TrainerConfig)

    evaluator.calc_and_write_all_tables(
        gdc_train=gdc_train,
        gdc_eval=gdc_eval_sc,
        trainer=trainer,
        table_path_score=EvalConfigSC.evaluation_scores_path,
        table_path_diff=EvalConfigSC.evaluation_diffs_path,
        cats_are_exclusive=True
    )

    evaluator.calc_and_write_all_tables(
        gdc_train=gdc_train,
        gdc_eval=gdc_eval_sm,
        trainer=trainer,
        table_path_score=EvalConfigSM.evaluation_scores_path,
        table_path_diff=EvalConfigSM.evaluation_diffs_path,
        cats_are_exclusive=True
    )

    # Evaluation where cats like positive and ambivalent are close to each other
    #
    # for gdi in gdc.gold_data_item_list:
    #
    #     score_dict_trainer = trainer.nlp(gdi.text).cats
    #     score_dict_gold = gdi.cats
    #
    #     score_total_trainer = None
    #     if score_dict_gold["T: positiv"] == 1:
    #         score_total_trainer = \
    #             score_dict_trainer["T: positiv"] \
    #             + score_dict_trainer["T: ambivalent"] * 0.5
    #     elif score_dict_gold["T: negativ"] == 1:
    #         score_total_trainer = \
    #             score_dict_trainer["T: negativ"] \
    #             + score_dict_trainer["T: ambivalent"] * 0.5
    #     elif score_dict_gold["T: ambivalent"] == 1:
    #         score_total_trainer = \
    #             score_dict_trainer["T: ambivalent"] \
    #             + score_dict_trainer["T: positiv"] * 0.5 \
    #             + score_dict_trainer["T: negativ"] * 0.5
    #     elif score_dict_gold["T: keine Tonalität ggü. KI, Algorithmen, Automatisierung"] == 1:
    #         score_total_trainer = score_dict_trainer["T: keine Tonalität ggü. KI, Algorithmen, Automatisierung"]
    #
    #     score_list.append(score_total_trainer)
    #
    # score_total_avg = sum(score_list) / len(score_list)


