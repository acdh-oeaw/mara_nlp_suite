import csv
from functools import reduce

import psycopg2
from psycopg2 import sql
from datetime import datetime

from psycopg2.extras import RealDictCursor

from etl import ske_manager, db_manager
from loggers import log_manager

# TODO: Maybe implement a check if in corp_info the compiled date has changed, because if so then the pos# could have been changed.
# Hannes message on this: Du kannst übrigens das compilationsdatum + uhrzeit abfragen
# und mit einem gespeicherten Wert vergleichen: corp_info?format=json&corpname=xxxx ->
# und dort den Wert unter compiled
# So lange dieser Wert konstant ist, ist klarerweise auch #pos' konsistent.

def index_articles(ske_config, db_config, index_table_name, trainer, table_name_ref_articles, should_do_dummy_run):

    if index_table_name is None or trainer is None or table_name_ref_articles is None:
        raise Exception("Necessary objects have not been initialized.")

    db_connection, db_cursor = db_manager.open_db_connection(db_config)

    def _init_index_table():

        log_manager.info_global("Checking if index table exists or if it needs to be created")
        pos_start = None

        db_cursor.execute(
            sql.SQL("""
                SELECT * 
                FROM information_schema.tables
                WHERE table_name = {index_table_name}
            """).format(
                index_table_name=sql.Literal(index_table_name)
            )
        )

        if db_cursor.rowcount == 1:

            log_manager.info_global(f"Index table exists, fetching highest pos to start / continue from")

            db_cursor.execute(
                sql.SQL("""
                    SELECT MAX(pos_mara002)
                    FROM {index_table_name}
                """).format(
                    index_table_name=sql.Identifier(index_table_name)
                )
            )

            pos_start = db_cursor.fetchone()["max"]
            if pos_start is None:
                # So that when asking in _populate_index_table for WHERE pos > pos_start, the zero element will be used too
                pos_start = -1

        else:

            log_manager.info_global(f"Index table does not exist, creating it and start from pos > -1")

            sql_cat_col_list = [sql.SQL("  {c} DECIMAL,\n").format(c=sql.Identifier(cat)) for cat in trainer.cats]
            sql_stmt_define_cat_cols = reduce(lambda a, b: a + b, sql_cat_col_list)

            sql_stmt_create_table = sql.SQL(
                "CREATE TABLE {index_table_name} (\n"
                "   pos_mara002 INT,\n"
                "{cols}"
                "   PRIMARY KEY (pos_mara002),"
                "   CONSTRAINT fkc FOREIGN KEY(pos_mara002) REFERENCES {table_name_ref_articles}(pos_mara002)"
                ")"
            ).format(
                index_table_name=sql.Identifier(index_table_name),
                cols=sql_stmt_define_cat_cols,
                table_name_ref_articles=sql.Identifier(table_name_ref_articles)
            )

            log_manager.info_global(f"create table sql statement:\n{sql_stmt_create_table.as_string(db_cursor)}")
            db_cursor.execute(sql_stmt_create_table)

            # So that when asking in _populate_index_table for WHERE pos > pos_start, the zero element will be used too
            pos_start = -1

        db_connection.commit()
        return pos_start


    def _populate_index_table(pos_start):

        log_manager.info_global(f"Start indexing at pos > {pos_start}")
        trainer.nlp.max_length = 3000000

        if should_do_dummy_run:
            limit = sql.SQL("LIMIT 20")
        else:
            limit = sql.SQL("")

        db_cursor.execute(
            sql.SQL("""
                SELECT * 
                FROM {table_name_ref_articles}
                WHERE pos_mara002 > {pos_start}
                ORDER BY pos_mara002
                {limit}
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles),
                pos_start=sql.Literal(pos_start),
                limit=limit
            )
        )

        pos_last = ske_manager.get_last_pos(ske_config)
        pos_percent_step = int((pos_last - pos_start) / 1000)
        pos_percent_current = pos_percent_step

        for dict_row in db_cursor.fetchall():

            pos = dict_row["pos_mara002"]

            if pos > pos_percent_current:
                log_manager.info_global(
                    f"Currently at {round(pos_percent_current / pos_percent_step / 10, 1)}% ; at pos {pos} out of {pos_last}"
                )
                pos_percent_current += pos_percent_step
                db_connection.commit()

            text = ske_manager.get_doc_from_pos(ske_config, pos)["text"]
            cats = trainer.nlp(text).cats

            sql_col_list = [sql.Identifier("pos_mara002")]
            sql_val_list = [sql.Literal(pos)]
            for k, v in cats.items():
                sql_col_list.append(sql.Identifier(k))
                sql_val_list.append(sql.Literal(round(v, 6)))
            sql_col_stmt = sql.SQL(", ").join(sql_col_list)
            sql_val_stmt = sql.SQL(", ").join(sql_val_list)

            db_cursor.execute(
                sql.SQL("""
                    INSERT INTO {index_table_name}
                    ({cols})
                    VALUES({vals})
                """).format(
                    index_table_name=sql.Identifier(index_table_name),
                    cols=sql_col_stmt,
                    vals=sql_val_stmt
                )
            )


    def _main():

        try:

            pos_start = _init_index_table()
            _populate_index_table(pos_start)

            db_connection.commit()
            ske_manager.close_session()

        except Exception as e:

            db_connection.rollback()
            ske_manager.close_session()
            raise e

        finally:
            db_manager.close_db_connection(db_connection, db_cursor)


    _main()


def index_sentences(ske_config, db_config, index_table_name, trainer, table_name_ref_articles, should_do_dummy_run):
    # TODO


    # 1. create table if not exists: db table:
        # id (FK to text_ref_sentences),
        # cat predictions (several),
        # already_annotated,
        # selected_on


    # 2. Make predictions

        # For each reference in text_ref_sentences

            # fetch whole article, cache it for reuse of next sentence

            # get sentences by using sent_start and sent_end

            # make predictions for each sentence

            # persist predictions

    pass
