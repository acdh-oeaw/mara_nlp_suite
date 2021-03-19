from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules
from pipelining import data_flow_registry
from IPython import embed
import main


ConfigRoot.articles_xml_directory = data_flow_registry.maxqdata_data["md1"]["articles_xml_directory"]
ConfigRoot.annotations_xlsx_file_path = data_flow_registry.maxqdata_data["md1"]["annotations_xlsx_file_path"]


class ConfigTransformArticles(ConfigRoot):

    maxqdata_gold_data_transform_function = data_flow_registry.gold_data["g1"]["maxqdata_specific_processing"]
    gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]


class ConfigTransformSentencesSm(ConfigRoot):

    maxqdata_gold_data_transform_function = data_flow_registry.gold_data["g2"]["maxqdata_specific_processing"]
    gold_data_json_path = data_flow_registry.gold_data["g2"]["path"]
    spacy_base_model = data_flow_registry.gold_data["g2"]["spacy_base_model"]


class ConfigTransformSentencesLg(ConfigRoot):

    maxqdata_gold_data_transform_function = data_flow_registry.gold_data["g3"]["maxqdata_specific_processing"]
    gold_data_json_path = data_flow_registry.gold_data["g3"]["path"]
    spacy_base_model = data_flow_registry.gold_data["g3"]["spacy_base_model"]


def run():

    gdc_articles = main.load_from_maxqdata(ConfigTransformArticles)
    gdc_sentences_sm = main.load_from_maxqdata(ConfigTransformSentencesSm)
    gdc_sentences_lg = main.load_from_maxqdata(ConfigTransformSentencesLg)

    main.persist_gold_data(ConfigTransformArticles, gdc_articles)
    main.persist_gold_data(ConfigTransformSentencesSm, gdc_sentences_sm)
    main.persist_gold_data(ConfigTransformSentencesLg, gdc_sentences_lg)

    embed()