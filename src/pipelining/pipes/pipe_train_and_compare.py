import csv
import math
from collections import OrderedDict
from psycopg2 import sql
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, ske_manager, db_manager
from pipelining import data_flow_registry
from IPython import embed
import main
import psycopg2


class ConfigTrainCompareBase(ConfigRoot):
    model_def_dict = data_flow_registry.models["mo7"]  # TODO: Adapt this

    trainer_class = model_def_dict["trainer_class"]
    train_data_cutoff = model_def_dict["train_data_cutoff"]
    iteration_limit = 1
    exclusive_classes = model_def_dict["exclusive_classes"]

    gold_data_json_path = data_flow_registry.gold_data[model_def_dict["source"][1]]["path"]
    gold_data_transform_rule = model_def_dict["gold_data_transform_rule"]

    should_persist_model = True


class ConfigTrainCompare1(ConfigTrainCompareBase):
    model_path = ConfigTrainCompareBase.model_def_dict["path"] + "_1"


class ConfigTrainCompare2(ConfigTrainCompareBase):
    model_path = ConfigTrainCompareBase.model_def_dict["path"] + "_2"


class ConfigIndexBase(ConfigRoot):

    should_load_model = True
    should_create_model = False
    should_persist_model = False

    indexing_function = data_flow_registry.model_compare_indices["mci1_1"]["index_creation_logic"]


class ConfigIndex1(ConfigIndexBase):
    index_dict = data_flow_registry.model_compare_indices["mci2_1"] # TODO: Adapt this
    index_table_name = index_dict["table_name"]


class ConfigIndex2(ConfigIndexBase):
    index_dict = data_flow_registry.model_compare_indices["mci2_2"] # TODO: Adapt this
    index_table_name = index_dict["table_name"]


def train(trainer1, trainer2):

    gdc = main.load_gold_data(ConfigTrainCompareBase)
    gdc = main.transform_gold_data(ConfigTrainCompareBase, gdc)

    if trainer1 is None:
        ConfigTrainCompareBase.should_load_model = False
        ConfigTrainCompareBase.should_create_model = True
        trainer1 = main.init_trainer(ConfigTrainCompare1, cats_list=gdc.cats_list)
        trainer2 = main.init_trainer(ConfigTrainCompare2, cats_list=gdc.cats_list)

    main.run_training(ConfigTrainCompare1, trainer1, gdc)
    main.run_training(ConfigTrainCompare2, trainer2, gdc)

    return trainer1, trainer2


def create_main_reference_table(db_cursor, db_connection, table_name_ref_articles_old, table_name_ref_articles_new):

    def fetch_random_ids():

        rand_limit = 1000

        sql_stmt = sql.SQL("""
            SELECT *
            FROM {table_name_ref_articles}
            ORDER BY RANDOM()
            LIMIT {rand_limit}
        """).format(
            table_name_ref_articles=sql.Identifier(table_name_ref_articles_old),
            rand_limit=sql.Literal(rand_limit),
        )

        db_cursor.execute(sql_stmt)
        random_set = [dict(row) for row in db_cursor.fetchall()]

        return random_set


    def init_random_main_reference_table(random_set):

        db_cursor.execute(
            sql.SQL("""
                DROP TABLE IF EXISTS {table_name_ref_articles} CASCADE
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles_new)
            )
        )

        db_cursor.execute(
            sql.SQL("""
                CREATE TABLE {table_name_ref_articles} (
                    doc_id VARCHAR NOT NULL,
                    pos_mara002 INT NOT NULL UNIQUE,
                    url_index1 VARCHAR,
                    CONSTRAINT {table_name_ref_articles_pk} PRIMARY KEY (doc_id)
                )
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles_new),
                table_name_ref_articles_pk=sql.Identifier(table_name_ref_articles_new + "_pk"),
            )
        )

        db_connection.commit()

        for random_row in random_set:

            sql_stmt = sql.SQL("""
                INSERT INTO {table_name_ref_articles} 
                (doc_id, pos_mara002, url_index1)
                VALUES ({doc_id}, {pos_mara002}, {url_index1})
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles_new),
                doc_id=sql.Literal(random_row["doc_id"]),
                pos_mara002=sql.Literal(random_row["pos_mara002"]),
                url_index1=sql.Literal(random_row["url_index1"]),
            )

            db_cursor.execute(sql_stmt)


    def main():
        random_set = fetch_random_ids()
        init_random_main_reference_table(random_set)
        db_connection.commit()

    main()

def drop_index(db_cursor, db_connection):

    for table_name in [ConfigIndex1.index_table_name, ConfigIndex2.index_table_name]:

        db_cursor.execute(
            sql.SQL("""
                DROP TABLE IF EXISTS {table_name} CASCADE
            """).format(
                table_name=sql.Identifier(table_name)
            )
        )

    db_connection.commit()


def create_index(trainer1, trainer2):
    # assign main reference table

    # ConfigTrainCompareBase.should_load_model = True
    # ConfigTrainCompareBase.should_create_model = False
    # ConfigTrainCompareBase.should_persist_model = False
    #
    # # necessary because "__dummy" is only added automatically when models are created, not when loaded:
    # if ConfigTrainCompareBase.should_do_dummy_run:
    #     ConfigTrainCompare1.model_path += "__dummy"
    #     ConfigTrainCompare2.model_path += "__dummy"
    #
    # trainer1 = main.init_trainer(ConfigTrainCompare1)
    # trainer2 = main.init_trainer(ConfigTrainCompare2)

    main.run_model_indexer(ConfigIndex1, trainer1)
    main.run_model_indexer(ConfigIndex2, trainer2)


def compare_index(db_cursor, main_iteration):

    def compare():

        table_name1 = ConfigIndex1.index_table_name
        table_name2 = ConfigIndex2.index_table_name

        # Two separat select statements because with a join there would be duplicated column names which get lost in the dictionary
        sql_stmt = sql.SQL("""
            SELECT *
            FROM {table_name1}
        """).format(
            table_name1=sql.Identifier(table_name1),
        )
        db_cursor.execute(sql_stmt)
        table_dicts1 = db_cursor.fetchall()

        sql_stmt = sql.SQL("""
            SELECT *
            FROM {table_name2}
        """).format(
            table_name2=sql.Identifier(table_name2),
        )
        db_cursor.execute(sql_stmt)
        table_dicts2 = db_cursor.fetchall()

        diff_dict = OrderedDict()
        for k in range(0, 11):
            diff_dict[k / 10] = []

        def calculcate_diff_avg_when_exclusive_class_true(cat_dict_1, cat_dict_2):

            min_list = []
            for (k1, v1), (k2, v2) in zip(cat_dict_1.items(), cat_dict_2.items()):
                if k1 == k2:
                    if k1 != "pos_mara002":
                        v1 = float(v1)
                        v2 = float(v2)
                        min_list.append(min(v1, v2))
                else:
                    raise Exception(f"Diverging columns detected in tables {table_name1} and {table_name2}")

            diff_avg = 1 - sum(min_list)

            return round(diff_avg, 1)

        def calculcate_diff_avg_when_exclusive_class_false(cat_dict_1, cat_dict_2):

            diff_list = []
            for (k1, v1), (k2, v2) in zip(cat_dict_1.items(), cat_dict_2.items()):
                if k1 == k2:
                    if k1 != "pos_mara002":
                        v1 = float(v1)
                        v2 = float(v2)
                        diff_list.append(abs(v1 - v2))
                else:
                    raise Exception(f"Diverging columns detected in tables {table_name1} and {table_name2}")

            diff_avg = sum(diff_list) / len(diff_list)
            return round(diff_avg, 1)

        func_calculcate_diff_avg = calculcate_diff_avg_when_exclusive_class_true  # TODO: Adapt this

        for r1, r2 in zip(table_dicts1, table_dicts2):

            if r1["pos_mara002"] != r2["pos_mara002"]:
                raise Exception(f"Different pos indices found in tables {table_name1} and {table_name2}")

            diff = func_calculcate_diff_avg(r1, r2)
            if diff < 0 or diff > 1:
                raise Exception(f"diff beyond sensible boundaries (0 and 1). Something must be wrong!. diff: {diff}")
            diff_dict[diff].append(r1["pos_mara002"])

        return diff_dict

    def write_to_csv(diff_dict):

        keys_list = list(diff_dict.keys())
        csv_rows = []
        file_write_mode = None

        if main_iteration == 0:
            file_write_mode = "w"
            csv_rows.append(["main_iteration"] + keys_list)
        else:
            file_write_mode = "a+"

        csv_rows.append([main_iteration] + [len(diff_dict[k]) for k in keys_list])

        with open("../data/duplicated_model_comparisons/diffs_mci2_1_mci2_2.csv", file_write_mode) as f:  # TODO: Adapt this
            w = csv.writer(f)
            w.writerows(csv_rows)

    def main():
        diff_dict = compare()
        write_to_csv(diff_dict)

    main()


def run():

    db_config = {
        "host": ConfigRoot.db_host,
        "dbname": ConfigRoot.db_name,
        "user": ConfigRoot.db_user,
        "password": ConfigRoot.db_password,
        "port": ConfigRoot.db_port
    }
    db_connection, db_cursor = db_manager.open_db_connection(db_config)

    table_name_ref_articles_old = ConfigIndexBase.table_name_ref_articles
    table_name_ref_articles_new = table_name_ref_articles_old + "_random_subset"
    ConfigIndexBase.table_name_ref_articles = table_name_ref_articles_new

    create_main_reference_table(db_cursor, db_connection, table_name_ref_articles_old, table_name_ref_articles_new)  # TODO: comment this out if not needed

    for i in range(100):

        if i == 0:
            trainer1 = None
            trainer2 = None

        trainer1, trainer2 = train(trainer1, trainer2) # TODO: comment this out if not needed
        drop_index(db_cursor, db_connection) # TODO: comment this out if not needed
        create_index(trainer1, trainer2) # TODO: comment this out if not needed
        compare_index(db_cursor, i) # TODO: comment this out if not needed

    db_manager.close_db_connection(db_connection, db_cursor)