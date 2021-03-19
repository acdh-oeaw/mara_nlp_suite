import psycopg2
from psycopg2 import sql
from typing import Tuple
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection
from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from loggers import log_manager
from etl import ske_manager


def open_db_connection(db_config, db_connection=None, db_cursor=None) -> Tuple[connection, RealDictCursor]:

    log_manager.debug_global("Checking for DB connection ...")

    if not db_connection or db_connection.closed != 0:

        log_manager.debug_global("Opening DB connection ...")
        db_connection = psycopg2.connect(
            host=db_config["host"],
            user=db_config["user"],
            database=db_config["dbname"],
            password=db_config["password"],
            port=db_config["port"]
        )

    if (db_connection and db_connection.closed == 0) and (not db_cursor or db_cursor.closed):

        log_manager.debug_global("Opening DB cursor ...")
        db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    return db_connection, db_cursor


def close_db_connection(db_connection, db_cursor):

    log_manager.debug_global("Closing DB connection and cursor ...")

    if db_cursor and not db_cursor.closed:
        db_cursor.close()

    if db_connection and db_connection.closed == 0:
        db_connection.close()


def get_prodigy_data(dataset_name, db_config, ske_config) -> GoldDataContainer:

    from prodigy.components.db import connect

    db = connect(db_id='postgresql', db_settings=db_config)

    prodigy_data = db.get_dataset(dataset_name)

    if not prodigy_data:
        log_manager.info_global(
            f"Dataset {dataset_name} doesn't exist in the prodigy database!"
        )
        return

    log_manager.info_global(f"Loaded {len(prodigy_data)} entries")

    prodigy_gold_data_container = transform_to_gold_data(prodigy_data, db_config, ske_config)

    return prodigy_gold_data_container


def transform_to_gold_data(prodigy_data, db_config, ske_config) -> GoldDataContainer:

    cats_list=[cats_dict["text"] for cats_dict in prodigy_data[0]["options"]]

    gold_data_item_list=[]

    # We open this here in case we need it to convert URLs to doc.ids (p2, p3, p4)
    db_connection, db_cursor = open_db_connection(db_config, None, None)

    for row in prodigy_data:

        if row['answer'] != 'accept':
            continue

        answers = row['accept']
        options = row['options']
        cats_assigned = {}

        for i, cat in enumerate(cats_list):

            idx = [ opt['id'] for opt in options if opt['text'] == cat ]

            if len(idx) == 0 or idx[0] not in answers:

                cats_assigned[cat] = 0

            else:

                cats_assigned[cat] = 1

        article_id = None

        # p1: doc.id = row['label'] as well as row['meta']['article_id']
        # p2, p3, p4: row['meta']['url] -> transform to doc.id via SKE or DB
        # p5: doc.id = row['meta']['docid']

        if 'article_id' in row['meta']: # p1
            article_id = row['meta']['article_id']
        elif 'docid' in row['meta']: # p5
            article_id = row['meta']['docid']
        elif 'url' in row['meta']: # p2, p3, p4
            # First we check whether there is an ID translation in the DB
            db_cursor.execute(
                sql.SQL("""
                    SELECT {col_docid}
                    FROM {tbl_ids}
                    WHERE {col_url} = %(url)s
                """).format(
                    col_docid = sql.Identifier('docid'),
                    tbl_ids = sql.Identifier('ske_docid_pos'),
                    col_url = sql.Identifier('url_index1')
                ),
                {
                    'url': row['meta']['url']
                }
            )
            result = db_cursor.fetchone()
            if result:
                article_id = result['docid']
            else:
                # If that fails, we prompt the SKE
                pos = ske_manager.get_pos_from_url(row['meta']['url'])
                article_id = ske_manager.get_docid_from_pos(ske_config, pos)
                # TODO: Ideally we would then insert this new ID translation into the DB
        else:
            raise Exception("Couldn't locate the annotation's text ID.")

        # TODO : Maybe add a text clean-up here to remove the abundant whitespace? Does it make a difference for spacy however?
        gold_data_item_list.append(
            GoldDataItem(
                article_id=article_id,
                text=row["text"] if 'text' in row else row['html'],
                cats=cats_assigned
            )
        )

    close_db_connection(db_connection, db_cursor)

    log_manager.info_global(f"Keeping {len(gold_data_item_list)} data items. ")

    return GoldDataContainer(cats_list=cats_list, gold_data_item_list=gold_data_item_list)
