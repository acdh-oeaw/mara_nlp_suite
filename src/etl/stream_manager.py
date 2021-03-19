import datetime
import json
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from loggers import log_manager
from etl import ske_manager, db_manager


def _select_text(db_connection, db_cursor, index_table_name, pk_column_name, pk_value):

    log_manager.debug_global(f"  Updating table '{index_table_name}' with the info that we selected this text at this time ...")

    db_cursor.execute(
        sql.SQL(
            "UPDATE {index_table_name} SET "
            # "already_selected = TRUE, " # left-over from the old system
            "selected_on = NOW() "
            "WHERE {pk} = %(pk_value)s "
        ).format(
            index_table_name = sql.Identifier(index_table_name),
            pk = sql.Identifier(pk_column_name)
        ),
        {'pk_value': pk_value}
    )
    db_connection.commit()


def get_cats_as_options(cats_as_list):

    cats_prodigy_format = []
    for i,c in enumerate(cats_as_list):
        cats_prodigy_format.append({"id": i, "text": c})

    return cats_prodigy_format


def _preselect_options(result):

    log_manager.debug_global("  Preselecting predicted options ...")

    # options for the user to select
    cats_as_options = get_cats_as_options(
        [
            c for c in result.keys()
            if c.startswith('AF:') or c.startswith('T:') or c.startswith('TI:')
        ]
        +
        [
            'VR: enthalten',
            'VR: nicht enthalten'
        ]
    )

    # options that are preselected based on model predictions
    options_accepted = []

    # meta information
    scores_text = ""

    for o in cats_as_options:

        cat = o["text"]

        # for predictions from index1
        if cat in result:
            cat_pred = result[cat]

            # TODO: this is only correct for independent labels!
            if cat_pred > 0.5:

                options_accepted.append(o["id"])

            scores_text += cat + ": " + str(round(cat_pred, 4)) + ", "

        # for index2
        elif cat == "VR: enthalten":
            # all scores > 0 should be marked as "VR enthalten"
            # all texts streamed from index2 will have a score > 0
            options_accepted.append(o["id"])

    return {
        'cats_as_options': cats_as_options,
        'options_accepted': options_accepted,
        'scores_text': scores_text
    }


def stream_from_db_with_predictions(ske_config, db_config, index_table_name):

    log_manager.debug_global("Streaming from DB with predictions ...")

    db_connection = None
    db_cursor = None

    (db_connection, db_cursor) = db_manager.open_db_connection(db_config, db_connection, db_cursor)

    try:

        while True:

            db_cursor.execute(
                sql.SQL(
                    'SELECT *, ("AF: Social Companions" + "AF: Soziale Medien") AS AF_SC_SM '
                    'FROM {index_table_name} '
                    'WHERE already_annotated = FALSE '
                    'AND already_selected = FALSE ' # left-over from the old system
                    "AND ((selected_on IS NULL) OR (selected_on < (NOW() - INTERVAL '2 days'))) "
                    'ORDER BY AF_SC_SM ASC '
                    'LIMIT 1'
                ).format(
                    index_table_name = sql.Identifier(index_table_name)
                )
            )

            result = db_cursor.fetchone()

            url = result["url"]

            _select_text(db_connection, db_cursor, index_table_name, 'url', url)

            options = _preselect_options(result)

            ske_doc = ske_manager.get_doc_from_url(ske_config, url)

            yield {
                "text": ske_doc["text"],
                "options": options['cats_as_options'],
                "accept": options['options_accepted'],
                "meta": {
                    "url": url,
                    "scores": options['scores_text']
                }
            }

    except Exception as ex:
        print(ex)

    finally:
        db_manager.close_db_connection(db_connection, db_cursor)


def stream_from_db_with_lmvr_keywords(ske_config, db_config, index1_table_name, index2_table_names, ske_translation_table_name):

    log_manager.debug_global("Streaming from database (index2) ...")

    # open db connection
    db_connection = None
    db_cursor = None

    (db_connection, db_cursor) = db_manager.open_db_connection(db_config, db_connection, db_cursor)
    # Don't know where to close the DB connection!

    while True:

        db_cursor.execute(
            sql.SQL("""
                SELECT *
                FROM {idx2_table} AS idx2
                INNER JOIN {ske_table} AS ske
                    ON ske.{ske_fk_idx2} = idx2.{idx2_fk_ske}
                INNER JOIN {idx1_table} AS idx1
                    ON idx1.{idx1_pk} = ske.{ske_fk_idx1}
                WHERE   idx1.already_annotated = FALSE
                    AND idx2.already_annotated = FALSE
                    AND idx1.already_selected = FALSE
                    AND ((idx1.selected_on IS NULL) OR (idx1.selected_on < (NOW() - INTERVAL '2 days')))
                    AND ((idx2.selected_on IS NULL) OR (idx2.selected_on < (NOW() - INTERVAL '2 days')))
                ORDER BY idx2.score_rarity_diversity DESC
                LIMIT 1
            """).format(
                idx2_table = sql.Identifier(index2_table_names['scores']),
                idx2_fk_ske = sql.Identifier('docid'),
                ske_table = sql.Identifier(ske_translation_table_name),
                ske_fk_idx2 = sql.Identifier('docid'),
                ske_fk_idx1 = sql.Identifier('url_index1'),
                idx1_table = sql.Identifier(index1_table_name),
                idx1_pk = sql.Identifier('url')
            )
        )

        result = db_cursor.fetchone()

        # log_manager.debug_global(f"Result={result}")

        url = result['url']
        docid = result['docid']
        # log_manager.debug_global(f"Selected text with url={url}, docid={docid}")

        # Store the information that this URL is getting selected now
        _select_text(db_connection, db_cursor, index1_table_name, 'url', url)
        _select_text(db_connection, db_cursor, index2_table_names['scores'], 'docid', docid)

        # Calculate the preselection options based on model predictions
        # (Will be empty if there are no predictions for this URL)
        options = _preselect_options(result)

        # Get this text's LMVR token counts
        db_cursor.execute(
            sql.SQL("""
                SELECT keyword_id, token_count
                FROM {tokens_table}
                WHERE docid = %(docid)s
                    AND token_count > 0
            """).format(
                tokens_table = sql.Identifier(index2_table_names['tokens']),
            ),
            {'docid': docid}
        )
        lmvr_count = { row['keyword_id']: int(row['token_count']) for row in db_cursor.fetchall() }
        lmvr_count_text = json.dumps(lmvr_count, ensure_ascii=False, sort_keys=True)

        # retrieving the text
        ske_doc = ske_manager.get_doc_from_url(ske_config, url)

        log_manager.debug_global("  Feeding this text into prodigy ...")

        yield {
            "text": ske_doc["text"],
            "options": options['cats_as_options'],
            "accept": options['options_accepted'],
            "meta": {
                "docid": result['docid'],
                "url": url,
                "category scores": options['scores_text'],
                "LMVR count": lmvr_count_text,
                "LMVR score": result['score_rarity_diversity']
            }
        }
