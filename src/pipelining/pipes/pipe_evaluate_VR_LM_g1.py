from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager, db_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4

import credentials
import json 

from psycopg2 import sql


import pandas as pd 



class ConfigLoadG1(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g1"]["path"] 

class ConfigTransformG1VR(ConfigRoot): 

    gold_data_transform_rule = gold_data_transform_rules.TransformRule7 # remove all categories other than VR

class ConfigTransformG1AF_Part1(ConfigRoot): 

    gold_data_transform_rule = gold_data_transform_rules.TransformRule2 # rename AF

class ConfigTransformG1AF_Part2(ConfigRoot): 

    gold_data_transform_rule = gold_data_transform_rules.TransformRule8 # remove all AF other than SM, SC


def run():

    # get the VR info  
    eval_data_container = main.load_gold_data(ConfigLoadG1)
    eval_data_container_VR = main.transform_gold_data(ConfigTransformG1VR, eval_data_container)
    df_VR = pd.DataFrame(
        data=[
            {
                "article_id": gdi.article_id, 
                "VR=ja": gdi.cats['Verantwortungsreferenz'] == 1,
            }
            for gdi in eval_data_container_VR.gold_data_item_list
        ]
    )

    # get the AF info 
    eval_data_container = main.load_gold_data(ConfigLoadG1)
    eval_data_container_AF = main.transform_gold_data(ConfigTransformG1AF_Part1, eval_data_container)
    #eval_data_container_AF = main.transform_gold_data(ConfigTransformG1AF_Part2, eval_data_container_AF)
    df_AF = pd.DataFrame(
        data=[
            {
                "article_id": gdi.article_id, 
                "AF=SM": gdi.cats['AF: Soziale Medien'] == 1, 
                "AF=SC": gdi.cats['AF: Social Companions'] == 1,
            }
            for gdi in eval_data_container_AF.gold_data_item_list
        ]
    )

    # for each text, read from the DB how many LM it contains 
    db_connection, db_cursor = db_manager.open_db_connection(db_config={
        "host": credentials.db_host,
        "dbname": credentials.db_name,
        "user": credentials.db_user,
        "password": credentials.db_password,
        "port": credentials.db_port
    })

    db_cursor.execute(
        sql.SQL("""
            select 
                t.docid as id, 
                count(distinct t.keyword_id) as dist, 
                sum(t.token_count) as total
            from {table_name} as t 
            where t.docid = any( %(docid_list)s )
            group by t.docid
            order by t.docid asc
        """).format(
            table_name = sql.Identifier('index_2__mara002__lmvr_tokens')
        ), 
        {
            'docid_list': [ gdi.article_id for gdi in eval_data_container.gold_data_item_list ], 
        }
    )
    results = db_cursor.fetchall()
    df_LM = pd.DataFrame(data=[
        {
            "article_id": r['id'], 
            "LMs total": r['total'], 
            "LMs distinct": r['dist'], 
        }
        for r in results
    ])

    # close db connection 
    db_manager.close_db_connection(db_connection, db_cursor)

    # merge the 3 dataframes 
    df = df_LM.merge(df_AF, how='outer', on='article_id')
    df = df.merge(df_VR, how='outer', on='article_id')
    # the LM table in the db doesn't contain all texts, so we have NaN values. Replace those with 0. 
    df['LMs total'] = df['LMs total'].fillna(0)
    df['LMs distinct'] = df['LMs distinct'].fillna(0)

    # define shortcuts to filter the dataframe 
    maskAF = (df['AF=SC'] == True) | (df['AF=SM'] == True)
    maskVR = (df['VR=ja'] == True)

    main.log_manager.info_global(
        "--------------------------------\n"
        "Calculations complete. \n"
        "You can now access the DataFrame as `df`. \n"
        "There are 2 masks provided as `maskAF` (SC or SM) and `maskVR` (trivial). \n"
    )

    # usage example: 
    # df[maskAF & maskVR]  
    # df[~maskVR]  

    embed()
