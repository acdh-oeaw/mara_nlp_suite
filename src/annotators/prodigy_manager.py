from loggers import log_manager
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from etl import stream_manager, db_manager


def run_recipe(db, stream, dataset_name, db_config, index1_table_name, index2_table_names):

    import prodigy

    @prodigy.recipe("cats_recipe")
    def choice():

        db_connection = None
        db_cursor = None

        # custom function to run when an annotation is complete
        def update(examples):

            log_manager.debug_global("Prodigy: updating ...")

            nonlocal db_connection
            nonlocal db_cursor

            db_connection, db_cursor = db_manager.open_db_connection(db_config, db_connection, db_cursor)

            assert db_connection and db_connection.closed == 0 # 0 means 'open'
            assert db_cursor and not db_cursor.closed

            for example in examples:
                try:

                    if index1_table_name and 'url' in example['meta']:
                        url = example['meta']['url']

                        log_manager.debug_global(f"Storing annotation meta info for url={url} in table {index1_table_name} ...")

                        db_cursor.execute(
                            sql.SQL(
                                "UPDATE {index_table_name} "
                                "SET already_annotated = TRUE "
                                "WHERE {pk} = %(value)s"
                            ).format(
                                index_table_name = sql.Identifier(index1_table_name),
                                pk = sql.Identifier('url')
                            ),
                            {'value': url}
                        )

                    # TODO: this could be made safer to ensure
                    # that index2 won't be updated accidentally with 'already_annotated'
                    # when we are actually only streaming from index1.
                    #
                    # Curently the stream from index1 does not set 'docid' in example['meta'],
                    # but this may not be good to rely on.
                    if index2_table_names and 'docid' in example['meta']:
                        docid = example['meta']['docid']

                        log_manager.debug_global(f"Storing annotation meta info for docid={docid} in table {index2_table_names['scores']} ...")

                        db_cursor.execute(
                            sql.SQL(
                                "UPDATE {index_table_name} "
                                "SET already_annotated = TRUE "
                                "WHERE {pk} = %(value)s"
                            ).format(
                                index_table_name = sql.Identifier(index2_table_names['scores']),
                                pk = sql.Identifier('docid')
                            ),
                            {'value': docid}
                        )

                    db_connection.commit()

                except Exception as ex:

                    log_manager.info_global(
                        f"Error storing an annotation in the database: {ex}"
                    )

                    db_connection.rollback()

        # custom function to run when the user exists prodigy
        # TODO: it is not ideal to put the closing of the database connection here because there might be multiple users.
        # but also, it won't hurt because the connection can be reopened at the next update,
        # and there is no better function to put it; see https://prodi.gy/docs/custom-recipes
        # at least, put here, it will close the connection when the last user stops annotating.
        def on_exit(controller):

            log_manager.debug_global("Prodigy: exiting ...")

            db_manager.close_db_connection(db_connection, db_cursor)


        return {
            "view_id": "choice",
            "dataset": dataset_name,
            "stream": stream,
            "db": db,
            "update": update,
            "on_exit": on_exit,
        }

    log_manager.debug_global("Starting up the prodigy server ...")

    prodigy.serve(
        "cats_recipe",
        host="0.0.0.0",
        choice_style="multiple",
    )


def run(ske_config, db_config, dataset_name, index1_table_name, index2_table_names=None, ske_translation_table_name=None):

    from prodigy.components.db import connect

    db = connect(db_id='postgresql', db_settings=db_config)

    # stream = stream_manager.stream_from_db_with_predictions(ske_config, db_config, index1_table_name)
    stream = stream_manager.stream_from_db_with_lmvr_keywords(ske_config, db_config, index1_table_name, index2_table_names, ske_translation_table_name)

    run_recipe(db, stream, dataset_name, db_config, index1_table_name, index2_table_names)
