import csv
import psycopg2
from psycopg2 import sql
from datetime import datetime

import spacy

from etl import ske_manager, db_manager
from loggers import log_manager
from psycopg2.extras import RealDictCursor
from typing import Dict


def init(
    db_config,
    ske_config,
    table_name_ref_articles=None,
    table_name_ref_sentences=None,
    spacy_base_model=None,
    should_do_dummy_run=False
):

    if table_name_ref_articles is None and table_name_ref_sentences is None:
        raise Exception("Both table_name_ref_articles and table_name_ref_sentences are None.")

    if table_name_ref_sentences is not None and spacy_base_model is None:
        raise Exception("For Sentence indexing, a spacy model is needed")

    db_connection, db_cursor = db_manager.open_db_connection(db_config)

    def _init_ref_table_articles():

        log_manager.info_global("Dropping and re-creating table for articles")

        db_cursor.execute(
            sql.SQL("""
                DROP TABLE IF EXISTS {table_name_ref_articles} CASCADE
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles),
            )
        )

        # TODO: Maybe remove column url_index1, I don't see an added benefit by it
        db_cursor.execute(
            sql.SQL("""
                CREATE TABLE {table_name_ref_articles} (
                    doc_id VARCHAR NOT NULL,
                    pos_mara002 INT NOT NULL UNIQUE,
                    url_index1 VARCHAR,
                    CONSTRAINT {table_name_ref_articles_pk} PRIMARY KEY (doc_id)
                )
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles),
                table_name_ref_articles_pk=sql.Identifier(table_name_ref_articles + "_pk"),
            )
        )

        db_connection.commit()


    def _populate_ref_table_articles():

        log_manager.info_global("Inserting references for all articles")

        pos_last = ske_manager.get_last_pos(ske_config)
        pos_percent_step = int(pos_last / 100)
        pos_percent_current = pos_percent_step

        for pos in ske_manager.iterate_over_pos_of_corpus(ske_config):

            if pos > pos_percent_current:
                log_manager.info_global(
                    f"Currently at {int(pos_percent_current / pos_percent_step)}% ; at pos {pos} out of {pos_last}"
                )
                pos_percent_current += pos_percent_step
                db_connection.commit()

            url = ske_manager.get_url_from_pos(ske_config, pos)
            doc_id = ske_manager.get_docid_from_pos(ske_config, pos)

            db_cursor.execute(
                sql.SQL("""
                    INSERT INTO {table_name_ref_articles} 
                    (doc_id, pos_mara002, url_index1)
                    VALUES ({doc_id}, {pos}, {url})
                """).format(
                    table_name_ref_articles=sql.Identifier(table_name_ref_articles),
                    doc_id=sql.Literal(doc_id),
                    pos=sql.Literal(pos),
                    url=sql.Literal(url),
                )
            )

            if should_do_dummy_run and pos > 5000:
                break


    def _init_ref_table_sentences():

        db_cursor.execute(
            sql.SQL("""
                DROP TABLE IF EXISTS {table_name_ref_sentences} CASCADE
            """).format(
                table_name_ref_sentences=sql.Identifier(table_name_ref_sentences),
            )
        )

        db_cursor.execute(
            sql.SQL("""
                CREATE TABLE {table_name_ref_sentences} (
                    doc_id VARCHAR NOT NULL,
                    sent_start INT NOT NULL,
                    CONSTRAINT doc_id_pk PRIMARY KEY (doc_id),
                    CONSTRAINT doc_id_fk FOREIGN KEY (doc_id) REFERENCES {table_name_ref_articles}(doc_id) 
                )
            """).format(
                table_name_ref_sentences=sql.Identifier(table_name_ref_sentences),
                table_name_ref_articles=sql.Identifier(table_name_ref_articles)
            )
        )

        db_connection.commit()


    def _populate_ref_table_sentences():
        # TODO

        nlp = spacy.load(spacy_base_model, disable=["tagger", "ner"])

        db_cursor.execute(
            sql.SQL("""
                SELECT doc_id FROM {table_name_ref_articles}
            """).format(
                table_name_ref_articles=sql.Identifier(table_name_ref_articles)
            )
        )
        for dict_row in db_cursor.fetchall():

            text = ske_manager.get_doc_from_docid(ske_config, dict_row["doc_id"])["text"]


    def _main():

        log_manager.info_global("Initialzing main reference tables")

        try:

            if table_name_ref_articles is not None:
                _init_ref_table_articles()
                _populate_ref_table_articles()

            # TODO
            # if table_name_ref_sentences is not None:
            #     _init_ref_table_sentences()
            #     _populate_ref_table_sentences()

            db_connection.commit()
            ske_manager.close_session()

        except Exception as e:

            db_connection.rollback()
            ske_manager.close_session()
            raise e

        finally:

            db_manager.close_db_connection(db_connection, db_cursor)


    _main()