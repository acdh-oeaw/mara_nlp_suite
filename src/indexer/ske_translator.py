import progress.bar
import psycopg2
from psycopg2 import sql

from etl import db_manager, ske_manager
from loggers import log_manager

def create_table(db_connection, db_cursor, table_name):

    try:

        log_manager.debug_global(f"Dropping table {table_name} ...")

        db_cursor.execute(
            sql.SQL("""
                DROP TABLE IF EXISTS {table};
            """).format(
                table = sql.Identifier(table_name)
            )
        )

        log_manager.debug_global(f"Creating table {table_name} ...")

        sql_stmt = sql.SQL("""
            CREATE TABLE {table} (
                {docid} varchar NOT NULL,
                {pos} varchar NOT NULL,
                {url} varchar NULL,
                CONSTRAINT ske_docid_pos_pk PRIMARY KEY ({docid}),
                CONSTRAINT ske_docid_pos_un_pos UNIQUE ({pos}),
                CONSTRAINT ske_docid_pos_un_url UNIQUE ({url})
            );
        """).format(
            table = sql.Identifier(table_name),
            docid = sql.Identifier('docid'),
            pos = sql.Identifier('pos_mara002'),
            url = sql.Identifier('url_index1')
        )

        db_cursor.execute(sql_stmt)

        db_connection.commit()

    except Exception as e:
        log_manager.info_global(f"There was an error: {e}")

        log_manager.debug_global(f"This was the SQL string: \n{sql_stmt.as_string(db_connection)}")

        log_manager.debug_global("Rolling back DB operations ...")
        db_connection.rollback()

        raise e

    return

def select_urls_from_index1(db_cursor, table_name, index1_table_name):

    db_cursor.execute(
        sql.SQL("""
            SELECT {index_pk}
            FROM {index} idx
            WHERE NOT EXISTS (
                SELECT {col}
                FROM {table} t
                WHERE t.{col} = idx.{index_pk}
            )
        """).format(
            index = sql.Identifier(index1_table_name),
            index_pk = sql.Identifier('url'),
            table = sql.Identifier(table_name),
            col = sql.Identifier('url_index1')
        )
    )

    return db_cursor.fetchall()

def select_docids_from_index2(db_cursor, table_name, index2_table_names):

    db_cursor.execute(
        sql.SQL("""
            SELECT {index_pk}
            FROM {index} idx
            WHERE NOT EXISTS (
                SELECT {col}
                FROM {table} t
                WHERE t.{col} = idx.{index_pk}
            )
        """).format(
            index = sql.Identifier(index2_table_names['scores']),
            index_pk = sql.Identifier('docid'),
            table = sql.Identifier(table_name),
            col = sql.Identifier('docid')
        )
    )

    return db_cursor.fetchall()

def insert_into_table(db_connection, db_cursor, table_name, docid, pos, url):

    try:

        db_cursor.execute(
            sql.SQL("""
                INSERT INTO {table}
                ({docid}, {pos}, {url})
                VALUES
                (%(docid)s, %(pos)s, %(url)s)
            """).format(
                table = sql.Identifier(table_name),
                docid = sql.Identifier('docid'),
                pos = sql.Identifier('pos_mara002'),
                url = sql.Identifier('url_index1'),
            ),
            {
                'docid': docid,
                'pos': pos,
                'url': url
            }
        )

        db_connection.commit()

    except Exception as e:

        db_connection.rollback()
        raise e

    return

def run(ske_config, db_config, docid_table_name, index1_table_name, index2_table_names, should_drop_create_table=False):

    (db_connection, db_cursor) = db_manager.open_db_connection(db_config)

    if should_drop_create_table:

        create_table(db_connection, db_cursor, docid_table_name)

    # Direction 1: look for URLs that are not yet in the translation table

    # Hannes says that pos -> docid is faster than docid -> pos
    # because the SKE uses pos as internal indices

    log_manager.debug_global("Looking for URLs ...")
    url_records = select_urls_from_index1(db_cursor, docid_table_name, index1_table_name)
    log_manager.info_global(f"Found {len(url_records)} URLs to be converted. ")

    if len(url_records) > 0:

        ske_manager.create_session(ske_config)

        progressbar = progress.bar.Bar('Converting URLs to docid',
            max=len(url_records),
            suffix='%(index)d/%(max)d done, ETA: %(eta_td)s h'
        )

        for record in url_records:
            url = record['url']
            pos = ske_manager.get_pos_from_url(url)
            docid = ske_manager.get_docid_from_pos(ske_config, pos) # this calls the API endpoing 'fullref'
            insert_into_table(db_connection, db_cursor, docid_table_name, docid, pos, url)
            progressbar.next()

        progressbar.finish()

    # Direction 2: look for docids that are not yet in the translation table

    log_manager.debug_global("Looking for docids ...")
    docid_records = select_docids_from_index2(db_cursor, docid_table_name, index2_table_names)
    log_manager.debug_global(f"Found {len(docid_records)} docids to be converted.")

    if len(docid_records) > 0:

        ske_manager.create_session(ske_config)

        progressbar = progress.bar.Bar('Converting docids to URLs',
            max=len(docid_records),
            suffix='%(index)d/%(max)d done, ETA: %(eta_td)s h'
        )

        for record in docid_records:
            docid = record['docid']
            pos = ske_manager.get_pos_from_docid(ske_config, docid) # this calls the API endpoint 'first'
            url = ske_manager.get_url_from_pos(ske_config, pos)
            insert_into_table(db_connection, db_cursor, docid_table_name, docid, pos, url)
            progressbar.next()

        progressbar.finish()

    # All set!

    ske_manager.close_session()

    db_manager.close_db_connection(db_connection, db_cursor)

    return
