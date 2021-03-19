from pipelining.pipe_root import ConfigRoot
import main

class ConfigSub(ConfigRoot):

    prodigy_dataset_name = "index_2__score_rarity_diversity_desc"

    index_table_name = "index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5"

    index_lmvr_table_names = {
        'keywords': 'index_2__mara002__lmvr_keywords',
        'scores': 'index_2__mara002__lmvr_scores',
        'tokens': 'index_2__mara002__lmvr_tokens'
    }

    ske_docid_url_table_name = 'ske_docid_pos'


def run():

    main.run_prodigy(ConfigSub)