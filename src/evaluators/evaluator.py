from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from trainer.abstract_trainer import AbstractTrainer
import csv


def create_predictions(gdc: GoldDataContainer, trainer: AbstractTrainer):

    article_preds_dict = {}
    for gdi in gdc.gold_data_item_list:
        article_preds_dict[gdi.article_id] = trainer.nlp(gdi.text).cats
    return article_preds_dict


def calc_diff_table(gdc_gold: GoldDataContainer, article_preds_dict):

    table_eval_pred = [
        ["Article ID"] \
        + [f"GOLD: {cat}" for cat in gdc_gold.cats_list] \
        + [f"PRED: {cat}" for cat in gdc_gold.cats_list] \
        + [f"AVG DIFF: {cat}" for cat in gdc_gold.cats_list] \
        + ["Average difference per article"]
    ]
    table_eval_pred.append(None)

    for gdi_eval in gdc_gold.gold_data_item_list:
        row = [gdi_eval.article_id]

        for cat in gdc_gold.cats_list:
            row.append(gdi_eval.cats[cat])

        cats_pred = article_preds_dict[gdi_eval.article_id]
        for cat in gdc_gold.cats_list:
            row.append(round(cats_pred[cat], 4))

        diff_list = []
        for cat in gdc_gold.cats_list:
            diff = round(abs(gdi_eval.cats[cat] - cats_pred[cat]), 4)
            diff_list.append(diff)
            row.append(diff)

        diff_avg = round(sum(diff_list) / len(diff_list), 4)
        row.append(diff_avg)
        table_eval_pred.append(row)

    table_row_avg = ["Average"]
    for col_i in range(1, len(table_eval_pred[0])):
        col_sum = 0
        for row in table_eval_pred[2:]:
            col_sum += row[col_i]
        col_avg = round(col_sum / len(table_eval_pred), 4)
        table_row_avg.append(col_avg)
    if len(table_row_avg) != len(table_eval_pred[0]):
        raise Exception
    table_eval_pred[1] = table_row_avg

    return table_eval_pred


def simplify_cat_predictions(article_preds_dict, cats_are_exclusive):

    for article_id, cats_pred in article_preds_dict.items():

        cats_pred_new = {}

        if cats_are_exclusive:

            max_val = 0
            max_cat = None

            for cat, val in cats_pred.items():
                if val > max_val:
                    max_val = val
                    max_cat = cat

            for cat in cats_pred.keys():
                if cat == max_cat:
                    cats_pred_new[cat] = 1
                else:
                    cats_pred_new[cat] = 0
        else:

            for cat, val in cats_pred.items():
                if val > 0.5:
                    cats_pred_new[cat] = 1
                else:
                    cats_pred_new[cat] = 0

        article_preds_dict[article_id] = cats_pred_new

    return article_preds_dict


def calc_score_table(
    gdc_train: GoldDataContainer,
    gdc_eval: GoldDataContainer,
    article_preds_dict,
):

    if gdc_train.cats_list != gdc_eval.cats_list:
        raise Exception

    table_scores = [
        [
            "Category",
            "Precision",
            "Recall",
            "F-Score",
            "True Positives",
            "False Positives",
            "True Negatives",
            "False Negatives",
            "Evaluation Positives",
            "Evaluation Negatives",
            "Training Positives",
            "Training Negatives",
        ]
    ]

    for cat in gdc_eval.cats_list:

        count_true_positive = 0
        count_false_positive = 0
        count_true_negative = 0
        count_false_negative = 0
        count_eval_positive = 0
        count_eval_negative = 0
        count_training_positive = 0
        count_training_negative = 0

        for gdi in gdc_eval.gold_data_item_list:

            pred_dict = article_preds_dict[gdi.article_id]

            score_pred = pred_dict[cat]
            score_eval = gdi.cats[cat]

            if score_pred == 1 and score_eval == 1:
                count_true_positive += 1
            elif score_pred == 1 and score_eval == 0:
                count_false_positive += 1
            elif score_pred == 0 and score_eval == 0:
                count_true_negative += 1
            elif score_pred == 0 and score_eval == 1:
                count_false_negative += 1

            if score_eval == 1:
                count_eval_positive += 1
            elif score_eval == 0:
                count_eval_negative += 1
            else:
                raise Exception

        for gdi in gdc_train.gold_data_item_list:

            score_train = gdi.cats[cat]

            if score_train == 1:
                count_training_positive += 1
            elif score_train == 0:
                count_training_negative += 1
            else:
                raise Exception

        if count_true_positive + count_false_positive > 0:
            precision = count_true_positive / (count_true_positive + count_false_positive)
        else:
            precision = 0
        if count_true_positive + count_false_negative > 0:
            recall = count_true_positive / (count_true_positive + count_false_negative)
        else:
            recall = 0
        if precision + recall > 0:
            f_score = 2 * (precision * recall) / (precision + recall)
        else:
            f_score = 0

        precision = round(precision, 4)
        recall = round(recall, 4)
        f_score = round(f_score, 4)

        table_scores.append(
            [
                cat,
                precision,
                recall,
                f_score,
                count_true_positive,
                count_false_positive,
                count_true_negative,
                count_false_negative,
                count_eval_positive,
                count_eval_negative,
                count_training_positive,
                count_training_negative,
            ]
        )

    return table_scores


def write_table(table, path):

    with open(path, "w") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerows(table)

def calc_and_write_all_tables(
    gdc_train: GoldDataContainer,
    gdc_eval: GoldDataContainer,
    trainer: AbstractTrainer,
    table_path_diff: str,
    table_path_score: str,
    cats_are_exclusive: bool,
):

    article_preds_dict = create_predictions(gdc_eval, trainer)
    table_diff = calc_diff_table(gdc_eval, article_preds_dict)
    write_table(table_diff, table_path_diff)

    article_preds_dict = simplify_cat_predictions(article_preds_dict, cats_are_exclusive)
    table_score = calc_score_table(gdc_train, gdc_eval, article_preds_dict)
    write_table(table_score, table_path_score)