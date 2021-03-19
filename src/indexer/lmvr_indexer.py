import datetime
import os
import pandas as pd
import progress.bar
import psycopg2
import re
import sqlalchemy
from psycopg2 import sql
from etl import db_manager, ske_manager
from loggers import log_manager

def create_progress_bar(title, max):

    return progress.bar.Bar(title,
        max=max,
        suffix='%(index)d/%(max)d done, ETA: %(eta_td)s h'
    )


def score_rarity_diversity(doc_df, keyword_df, token_df):
    # This algorithm favors rare keywords over frequent keywords,
    #   and many types over many tokens,
    #   but also many tokens over few tokens.
    #
    # score(text) =
    #   sum for each keyword k:
    #     sum for n from 1 to the token count of k in text:
    #       (1/corpus token count of k) * (1/n)
    #
    # A keyword with a high token count in the corpus will yield a smaller coefficient, and vice versa,
    #   thus favoring rarity.
    # A text t1 where keyword k appears n times will have a lower score
    #   than a text t2 where k appears n+1 times, if t1 and t2 are otherwise identical,
    #   thus favoring higher token counts.
    # A text t1 where keyword k1 appears n times and keyword k2 appears m times,
    #   where k1 and k2 have the same corpus token count, will have a higher score
    #   than a text t2 where k1 appears n+l times and k2 appears m-l times,
    #   thus favoring diversity.

    log_manager.debug_global("Calculating rarity/diversity scores ...")

    # We select the column 'score_rarity_diversity', which as of now contains only 0s.
    # This returns a Series object whose index is the docids (the index of doc_df).
    scores = doc_df['score_rarity_diversity']

    bar = create_progress_bar('Computing scores per keyword', keyword_df.shape[0])

    # iterate over rows in keyword_df
    for kw, data in keyword_df.iterrows():
        # kw is the label of the row (the keyword_id)
        # data is a Series of the values in this row

        # get this keyword's corpus token count
        # we will use this to calculate its inverse frequency
        kw_freq = data.corpus_count

        # get this keyword's token count per text
        try:
            # token_df has a MultiIndex: 1st the keyword_id, 2nd the docid
            # We select all rows with keyword_id = kw. This returns a DataFrame.
            # Then we select only the column 'token_count'. This returns a Series.
            tokencounts = token_df.loc[kw]['token_count']
            # tokencounts is a Series, indexed with docid,
            #   containing as values the token counts of kw in the given docid

        except KeyError as e:
            tokencounts = pd.Series(index=doc_df.index, data=0)

        # This is the formula:
        def calculate_score(token_count, kw_freq):
            return sum(map(lambda x: pow(kw_freq, -1) * pow(x, -1),
                           range(1, int(token_count)+1)))

        # Apply this function to the token counts of the current keyword.
        scores = scores.add(
            tokencounts.apply(calculate_score, args=(kw_freq,)),
            fill_value=0.0
        )

        bar.next()

    bar.finish()

    # feed the temporary Series back into the table
    doc_df['score_rarity_diversity'] = scores

    # sort by highest score
    doc_df = doc_df.sort_values(by='score_rarity_diversity', ascending=False)

    return doc_df


def create_tables(db_config, index1_table_name, index2_table_names):

    (db_connection, db_cursor) = db_manager.open_db_connection(db_config)

    try:

        log_manager.debug_global("Dropping tables ...")
        db_cursor.execute(
            sql.SQL("""
                DROP TABLE IF EXISTS {table_keywords}, {table_scores}, {table_tokens} CASCADE;
                DROP INDEX IF EXISTS {score_idx} CASCADE;
            """).format(
                table_keywords = sql.Identifier(index2_table_names['keywords']),
                table_scores = sql.Identifier(index2_table_names['scores']),
                table_tokens = sql.Identifier(index2_table_names['tokens']),
                score_idx = sql.Identifier('index_2__mara002__lmvr_scores_score_rarity_diversity_idx')
            )
        )


        # table 1: keywords
        log_manager.debug_global(f"Creating table {index2_table_names['keywords']} ...")

        db_cursor.execute(
            sql.SQL("""
                CREATE TABLE {table} (
                    {pk} varchar NOT NULL,
                    corpus_count int4 NOT NULL,
                    category varchar NOT NULL,
                    CONSTRAINT index_2__mara002__lmvr_keywords_pk PRIMARY KEY ({pk})
                );
            """).format(
                table =sql.Identifier(index2_table_names['keywords']),
                pk = sql.Identifier('keyword_id')
            )
        )

        # table 2: texts + scores
        log_manager.debug_global(f"Creating table {index2_table_names['scores']} ...")

        db_cursor.execute(
            sql.SQL("""
                CREATE TABLE {table} (
                    {pk} varchar NOT NULL,
                    {score1} numeric NOT NULL,
                    already_annotated bool NULL,
                    selected_on timestamptz NULL,
                    CONSTRAINT index_2__mara002__lmvr_scores_pk PRIMARY KEY ({pk})
                );
                CREATE INDEX index_2__mara002__lmvr_scores_score_rarity_diversity_idx
                    ON {table}
                    USING btree
                    ({score1} DESC);
            """).format(
                table = sql.Identifier(index2_table_names['scores']),
                pk = sql.Identifier('docid'),
                score1 = sql.Identifier('score_rarity_diversity')
            )
        )

        # table 3: keywords in texts
        log_manager.debug_global(f"Creating table {index2_table_names['tokens']} ...")

        db_cursor.execute(
            sql.SQL("""
                CREATE TABLE {table} (
                    {fk_texts} varchar NOT NULL,
                    {fk_kw} varchar NOT NULL,
                    token_count int4 NOT NULL DEFAULT 0,
                    CONSTRAINT index_2__mara002__lmvr_tokens_pk PRIMARY KEY ({fk_texts}, {fk_kw}),
                    CONSTRAINT index_2__mara002__lmvr_tokens_fk FOREIGN KEY ({fk_texts})
                        REFERENCES {table_texts}({fk_texts})
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                    CONSTRAINT index_2__mara002__lmvr_tokens_fk_keyword FOREIGN KEY ({fk_kw})
                        REFERENCES {table_kw}({fk_kw})
                        ON UPDATE CASCADE
                        ON DELETE CASCADE
                );
            """).format(
                table = sql.Identifier(index2_table_names['tokens']),
                table_texts = sql.Identifier(index2_table_names['scores']),
                fk_texts = sql.Identifier('docid'),
                table_kw = sql.Identifier(index2_table_names['keywords']),
                fk_kw = sql.Identifier('keyword_id')
            )
        )

        db_connection.commit()

    except Exception as e:

        db_connection.rollback()
        raise e

    finally:
        db_manager.close_db_connection(db_connection, db_cursor)

    return # TODO: Is this empty return on purpose?


def write_df_to_db(df, index_table_name, db_config):

    log_manager.debug_global("Creating SqlAlchemy engine ...")

    engine = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL(
            'postgresql+psycopg2',
            host=db_config['host'],
            port=db_config['port'],
            username=db_config['user'],
            password=db_config['password'],
            database=db_config['dbname']
        )
    )

    try:
        log_manager.debug_global(f"Writing DataFrame to DB {index_table_name} ...")

        df.to_sql(index_table_name, engine, if_exists='append')

    except ValueError as e:
        log_manager.info_global(f"Can't write DataFrame to Database: table {index_table_name} already exists")

    finally:
        log_manager.debug_global("Disposing of SqlAlchemy engine ...")

        engine.dispose()


def read_keyword_df(data_path):
    # for each keyword, store its token count in the entire corpus

    # we extract keywords and their token count from the filenames in the DOCIDS folder
    # the column 'csv_types' points to the CSV file that contains the doc ids where this keyword appears
    keyword_df = pd.DataFrame({
        'csv_types': os.listdir(f'{data_path}/DOCIDS')
    })
    # set up a regex pattern to extract information out of the file name
    pattern = re.compile(r'docids_(freqs_(.*)_id_word_0_0_0_mara002)_n_([0-9]+)\.csv')
    # group 1 is the name of the CSV file containing the tokens, minus the extension '.csv'
    # group 2 is the keywords ID, consisting of a number and a human-readable representation
    # group 3 is the token count of this keyword in the entire corpus
    csv_tokens = []
    ids = []
    counts = []
    # iterate over the keywords
    for value in keyword_df['csv_types']:
        match = pattern.fullmatch(value)
        try:
            # store the group values
            csv_tokens.append(match.group(1) + '.csv')
            ids.append(match.group(2))
            counts.append(int(match.group(3)))

        except AttributeError as e:
            log_manager.info_global(f"Unexpected file name: {value} \nDid not match the RegEx pattern.")
            # store null values
            csv_tokens.append(None)
            ids.append(None)
            counts.append(None)

    # the column 'csv_tokens' points to the CSV files that contain
    # all doc ids where each keyword appears, together with its token count within that document
    keyword_df['csv_tokens'] = csv_tokens

    # the column 'token_count' contains the keywords' token count in the entire corpus
    keyword_df['corpus_count'] = counts

    keyword_df['keyword_id'] = ids

    keyword_df['category'] = keyword_df['keyword_id'].apply(
        lambda x: 'SM' if int(x[0:2]) >= 42 else 'SC' if int(x[0:2]) >= 30 else 'Allgemein'
    )

    # set the keywords' IDs as the DF's row labels
    keyword_df = keyword_df.set_index('keyword_id')


    return keyword_df # with the column 'csv_tokens'


def run(data_path, db_config, index1_table_name, index2_table_names, ske_config):

    start = datetime.datetime.now()
    log_manager.info_global("--------------------------------")
    log_manager.info_global(f"{start.strftime('[%y-%m-%d %H:%M:%S]')} START INDEXING\n")

    log_manager.info_global("Creating DB tables ...")

    create_tables(db_config, index1_table_name, index2_table_names)

    log_manager.info_global("Creating DataFrames from original CSV files ...")

    # 1. set up the keywords dataframe
    log_manager.debug_global("Creating DataFrame for keywords ...")
    keyword_df = read_keyword_df(data_path)

    # store the keywords df to the database
    log_manager.debug_global("Writing keywords DF to DB ...")
    write_df_to_db(
        keyword_df.drop(columns=['csv_tokens', 'csv_types'], inplace=False),
        index2_table_names['keywords'],
        db_config
    )


    # 2. set up the text token counts dataframe
    log_manager.debug_global("Creating DataFrame for token counts ...")
    token_df = pd.DataFrame()

    # in doc_df, we create a column for each keyword
    # and fill it with that keyword's token count in the given document
    bar = create_progress_bar('Calculating total of tokens per text', keyword_df.shape[0])

    for kw in keyword_df.itertuples():
        # kw is a Pandas object representing the row
        # we find the token counts in the CSV file stored in the column 'csv_tokens' of keyword_df
        temp_df = pd.read_csv(
            f'{data_path}/CSV/{kw.csv_tokens}', sep='\t', skiprows=8,
            names=['docid', 'token', 'token_count'], usecols=['docid', 'token_count']
        )
        # we need to group by doc id and sum all the token counts for various shapes of the token
        temp_df = temp_df.groupby(['docid'], as_index=False).sum()

        # add a column
        temp_df['keyword_id'] = kw.Index

        temp_df = temp_df.set_index(['keyword_id', 'docid'], verify_integrity=True)
            # 1st index: keyword_id, because this allows for fewer lookups when calculating the scores

        # we append the rows to token_df
        token_df = token_df.append(temp_df, verify_integrity=True)

        bar.next()
    bar.finish()

    # Don't write to token_df to DB yet because it has a FK constraint to doc_df.


    # 3. set up the texts dataframe
    log_manager.debug_global("Creating DataFrame for texts ...")

    # we use this file only to get a complete list of doc ids
    doc_df = pd.read_csv(
        f'{data_path}/mara002_kvr_all.docids.counts.csv', sep='\t',
        names=['types_count', 'docid'], usecols=['docid']
    )
    doc_df['score_rarity_diversity'] = 0.0
    doc_df['already_annotated'] = False
    doc_df['selected_on'] = None
    doc_df = doc_df.set_index('docid')

    # Calculate scores
    log_manager.debug_global("Calculating scores for texts ...")

    doc_df = score_rarity_diversity(doc_df, keyword_df, token_df)

    # Write doc_df to DB
    log_manager.debug_global("Writing DF for texts to DB ...")

    write_df_to_db(
        doc_df,
        index2_table_names['scores'],
        db_config
    )

    # Now we can write token_df to the DB.
    log_manager.debug_global("Writing DF for tokens to DB ...")

    write_df_to_db(
        token_df,
        index2_table_names['tokens'],
        db_config
    )


    # all done!
    end = datetime.datetime.now()
    log_manager.info_global(f"{end.strftime('[%y-%m-%d %H:%M:%S]')} DONE INDEXING, duration: {end-start}")

    return # TODO: Is this empty return on purpose?
