from etl.gold_data_manager import GoldDataContainer, GoldDataItem
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4

import credentials
import json 
from typing import List, Dict, Set, Tuple, Generator, Type

import pandas as pd 

class ConfigLoadP5(ConfigRoot):

    prodigy_dataset_name = data_flow_registry.prodigy_data["p5"]["dataset_name"] 

def run():

    import prodigy.components.db

    db = prodigy.components.db.connect(db_id='postgresql', db_settings={
        "host": credentials.db_host,
        "dbname": credentials.db_name,
        "user": credentials.db_user,
        "password": credentials.db_password,
        "port": credentials.db_port
    })
    prodigy_data = db.get_dataset(ConfigLoadP5.prodigy_dataset_name)

    df = pd.DataFrame( 
        data=[
            {
                "article_id": pd['meta']['docid'], 
                "answer": pd['answer'], 
                "AF=SC": len([ a for a in pd['accept'] for c in pd['options'] if a == c['id'] and c['text'] == 'AF: Social Companions' ]) == 1, 
                "AF=SM": len([ a for a in pd['accept'] for c in pd['options'] if a == c['id'] and c['text'] == 'AF: Soziale Medien' ]) == 1, 
                "VR=ja": len([ a for a in pd['accept'] for c in pd['options'] if a == c['id'] and c['text'] == 'VR: enthalten' ]) == 1, 
                "LMs total": sum(json.loads(pd['meta']['LMVR count']).values()), 
                "LMs distinct": len(json.loads(pd['meta']['LMVR count'])), 
                "LMs": json.loads(pd['meta']['LMVR count'])
            }
            for pd in prodigy_data 
        ]
    )

    # remove rows where answer='reject'
    df = df[df.answer == 'accept']

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
    # df[maskAF & maskVR] # yields 45 rows 
    # df[maskAF & ~maskVR] # yields 57 rows 

    embed()
