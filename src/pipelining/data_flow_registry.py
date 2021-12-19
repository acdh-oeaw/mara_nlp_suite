from etl import maxqdata_manager
from etl.gold_data_transform_rules import *
from indexer import model_indexer
from trainer.trainer4 import Trainer4

amc_corpora = None
maxqdata_data = None
prodigy_data = None
gold_data = None
models = None
model_indices = None
lmvr = None
evaluations = None


amc_corpora = {
    "mara002": {
        "source": "Full AMC -> Hannes' keyword selection",
        "size": "45k ske docs",
        "info_url": "http://ske.herkules.arz.oeaw.ac.at/run.cgi/corp_info?corpname=mara002&struct_attr_stats=1&subcorpora=1"
    },
    "mara002_1500": {
        "source": "mara002 -> random selection of 1500 articles",
        "size": "1500 ske docs",
        "info_url": "http://ske.herkules.arz.oeaw.ac.at/run.cgi/corp_info?corpname=mara002_1500&struct_attr_stats=1&subcorpora=1"
    },
}

maxqdata_data = {
    "md1": {
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-02-21/nlp_import/",
        "annotations_xlsx_file_path": "../data/maxqdata_data/annotations_maxqdata/2020-04-04/MARA_Full sample _1250320_V1.mx18.xlsx",
        "text_labels": "181 labels (with redundancies due to technical limitations in maxqdata)",
        "source": (amc_corpora, "mara002_1500"),
        "size": "1499 articles, 13282 annotations.",
        "description": "First batch"
    },
    "md2": { # Probecodierung mit 50 Texten # TODO
    },
    "md3": {
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-12-17_Vertiefungsanalyse/101_derived/mara_SocialCompanions/",
        "annotations_xlsx_file_path": "../data/maxqdata_data/annotations_maxqdata/2021-05-27_Vertiefungsanalyse/Codierung_SC_Final.xlsx",
        "source": (models, ""), # TODO which models / indices were used?
        "source_selection_logic": "'AF: Social Companions' between 0.99983 and 0.505869, 'TI: Hauptthema' between 1.00000 and 0.562652, LMVR-logic", # see redmine ticket #18496
        "size": "270 articles",
        "description": "Vertiefungsanalyse SC: Social Companions"
    },
    "md4": {
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-12-17_Vertiefungsanalyse/101_derived/mara_SozialeMedien/",
        "annotations_xlsx_file_path": "../data/maxqdata_data/annotations_maxqdata/2021-05-27_Vertiefungsanalyse/Codierung_SM_Final.xlsx",
        "source": (models, ""), # TODO which models / indices were used?
        "source_selection_logic": "'AF: Soziale Medien' between 0.999896 and 0.72494, 'TI: Hauptthema' between 1.000000 and 0.515524, LMVR-logic", # see redmine ticket #18496
        "size": "270 articles",
        "description": "Vertiefungsanalyse SM: Social Media"
    },
    "md5": {
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-12-17_Vertiefungsanalyse/101_derived/mara_SozialeMedien_SocialCompanions/",
        "annotations_xlsx_file_path": None,
        "source": (models, ""), # TODO which models / indices were used?
        "source_selection_logic": "'AF: Soziale Medien' and 'AF: Social Companions' above 0.9, 'TI: Hauptthema' between 1.0 and 0.991806, LMVR-logic", # see redmine ticket #18496
        "size": "10 articles",
        "description": "Vertiefungsanalyse SM+SC: Social Media and Social Companions"
    }
}

prodigy_data = {
    "p1": {
        "dataset_name": "p1", #formerly s2
        "text_labels": "'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
        "source": "No index used here.",
        "source_selection_logic": ( # TODO: Fetch logic from git history, re-integrate it into current code so that it can be referenced here and re-run.
            "This first iteration was done by randomly selecting 5 texts from corpus amc_corpora['mara002_1500']."
            "Out of each random selection one text was served to the annotator based on highest scores"
            "from models['mo1'] (where only the two main AF were regarded)"
        ),
        "size": "311 articles",
    },
    "p2": {
        "dataset_name": "p2", #formerly s3
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität",
        "source": (model_indices, ["i1", "i2", "i3"]),
        "source_selection_logic": "sort by SC+SM desc",
        "size": "412 articles",
    },
    "p3": {
        "dataset_name": "p3", #formerly s4
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität",
        "source": (model_indices, ["i1", "i2", "i3"]),
        "source_selection_logic": "sort by SM desc",
        "size": "202 articles",
    },
    "p4": {
        "dataset_name": "p4", #formerly s5
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität, 'af_sc_sm'", # TODO: In the prodigy dataset is an additional label 'af_sc_sm'; investigate
        "source": (model_indices, ["i1", "i2", "i3"]),
        "source_selection_logic": "sort by SC+SM asc",
        "size": "392 articles",
    },
    "p5": {
        "dataset_name": "p5", #formerly s6
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität, 'VR: enthalten', 'VR: nicht enthalten'",
        "source": "", # TODO: Reference the LMVR index once that is defined here.
        "source_selection_logic": None, # TODO: Fetch logic from git history, re-integrate it into current code so that it can be referenced here and re-run.
        "size": "300 articles",
    },
}

gold_data = {
    "g1": {
        "path": "../data/gold_data/g1.json",
        "text_labels": "181 labels",
        "source": (maxqdata_data, "md1"),
        "size": "1499 full articles",
        "maxqdata_specific_processing": maxqdata_manager.transform_to_gold_data_articles,
    },
    "g2": {
        "path": "../data/gold_data/g2.json",
        "text_labels": "181 labels",
        "source": (maxqdata_data, "md1"),
        "size": "60208 sentences",
        "maxqdata_specific_processing": maxqdata_manager.transform_to_gold_data_sentences,
        "sentence_split_logic": "spacy's nlp sentencizer, using spacy_base_model",
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4"
    },
    "g3": {
        "path": "../data/gold_data/g3.json",
        "text_labels": "181 labels",
        "source": (maxqdata_data, "md1"),
        "size": "40316 sentences",
        "maxqdata_specific_processing": maxqdata_manager.transform_to_gold_data_sentences,
        "sentence_split_logic": "spacy's nlp sentencizer, using spacy_base_model",
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.3.0"
    },
    "g4": {
        "path": "../data/gold_data/g4.json",
        "text_labels": "'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
        "source": (prodigy_data, "p1"),
        "size": "302 full articles (excluding 9 from p1 where the answer was not 'accept')",
    },
    "g5": {
        "path": "../data/gold_data/g5.json",
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität",
        "source": (prodigy_data, "p2"),
        "size": "410 full articles (excluding 2 from p2 where the answer was not 'accept')",
    },
    "g6": {
        "path": "../data/gold_data/g6.json",
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität",
        "source": (prodigy_data, "p3"),
        "size": "202 full articles (excluding none from p3)",
    },
    "g7": {
        "path": "../data/gold_data/g7.json",
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität, 'af_sc_sm'",
        "source": (prodigy_data, "p4"),
        "size": "392 full articles (excluding none from p4)",
    },
    "g8": {
        "path": "../data/gold_data/g8.json",
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität, 'VR: enthalten', 'VR: nicht enthalten'",
        "source": (prodigy_data, "p5"),
        "size": "300 full articles (excluding none from p5)",
    },
    "g9": { # Vertiefungsanalyse 'Social Companions'
        "path": "../data/gold_data/g9.json",
        "maxqdata_specific_processing": maxqdata_manager.transform_to_gold_data_articles,
        "source": (maxqdata_data, "md3"),
        "size": "270 articles",
    },
    "g10": { # Vertiefungsanalyse 'Social Media'
        "path": "../data/gold_data/g10.json",
        "maxqdata_specific_processing": maxqdata_manager.transform_to_gold_data_articles,
        "source": (maxqdata_data, "md4"),
        "size": "270 articles",
    },
}

models = {
    "mo1": {
        "path": "../data/models/mo1", #TODO : Fetch from git history
        "text_labels": "Anwendungsfelder: 'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule1,
        "train_data_cutoff": 100,
        "iteration_limit": 40, #TODO: this is an assumption. Check with git history what the iteration was back then
        "exclusive_classes": None, #TODO
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo2": {
        "path": "../data/models/mo2", #TODO : Fetch from git history
        "text_labels": "Anwendungsfelder: 'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule1,
        "train_data_cutoff": 50,
        "iteration_limit": None, #TODO
        "exclusive_classes": None, #TODO
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo3": {
        "path": "../data/models/mo3", #formerly t4__tdc100__s1_articles__tr2_1__sc_sm_alle_anwendungsfelder or t4__tdc100__s1__tr2_1__sc_sm_alle_anwendungsfelder
        "text_labels": "Anwendungsfelder: 'AF: Social Companions', 'AF: Soziale Medien', and all other 31 AF",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule2,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": False,
        "train_data_size": 1471,
        "train_data_hash": 311100072,
        "eval_data_hash": 3211313,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo4": {
        "path": "../data/models/mo4", #formerly t4__tdc50__s1_articles__tr2_1__sc_sm_alle_anwendungsfelder or t4__tdc50__s1__tr2_1__sc_sm_alle_anwendungsfelder
        "text_labels": "Anwendungsfelder: 'AF: Social Companions', 'AF: Soziale Medien', and all other 31 AF",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule2,
        "train_data_cutoff": 50,
        "iteration_limit": 30,
        "exclusive_classes": False,
        "train_data_size": 736,
        "train_data_hash": 311165603,
        "eval_data_hash": 312672931,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo5": {
        "path": "../data/models/mo5", #formerly t4__tdc100__s1_articles__tr3__tonalitaet or t4__tdc100__s1__tr3__tonalitaet
        "text_labels": "Tonalität: 'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule3,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "train_data_size": 1471,
        "train_data_hash": 311100072,
        "eval_data_hash": 3211313,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo6": {
        "path": "../data/models/mo6", #formerly t4__tdc50__s1_articles__tr3__tonalitaet or t4__tdc50__s1__tr3__tonalitaet
        "text_labels": "Tonalität: 'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule3,
        "train_data_cutoff": 50,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "train_data_size": 736,
        "train_data_hash": 311165603,
        "eval_data_hash": 312672931,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo7": {
        "path": "../data/models/mo7", #formerly t4__tdc100__s1_articles__tr5__thematisierungsintensitaet or t4__tdc100__s1__tr5__thematisierungsintensitaet
        "text_labels": "Thematisierungsintensität: 'TI: Hauptthema', 'TI: Nebenthema', 'TI: Verweis'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule5,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "train_data_size": 1471,
        "train_data_hash": 311100072,
        "eval_data_hash": 3211313,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo8": {
        "path": "../data/models/mo8", #formerly t4__tdc50__s1_articles__tr5__thematisierungsintensitaet or t4__tdc50__s1__tr5__thematisierungsintensitaet
        "text_labels": "Thematisierungsintensität: 'TI: Hauptthema', 'TI: Nebenthema', 'TI: Verweis'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule5,
        "train_data_cutoff": 50,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "train_data_size": 736,
        "train_data_hash": 311165603,
        "eval_data_hash": 312672931,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo9": { # biggest model for 'Anwendungsfelder', merged from several sources
        "path": "../data/models/mo9", # formerly t4__tdc100__s1_articles_tr2_1_tr8__s2_tr9__s3_tr8__s4_tr8__s5_tr8__s6_tr8 , where sX means dataset and trX means TransformationRule
        "text_labels": "Anwendungsfelder: 'AF: Social Companions', 'AF: Soziale Medien'",
        "source": [(gold_data, "g1"), (gold_data, "g4"), (gold_data, "g5"), (gold_data, "g6"), (gold_data, "g7"), (gold_data, "g8")],
        "trainer_class": Trainer4,
        "gold_data_transform_rule": [(TransformRule2, TransformRule8), TransformRule9, TransformRule8, TransformRule8, TransformRule8, TransformRule8],
        "train_data_cutoff": 100,
        "iteration_limit": 20,
        "exclusive_classes": False,
        "train_data_size": 3105,
        "train_data_hash": 312607402,
        "eval_data_hash": 3211313,
        "spacy_version": "2.3",
    },
    "mo10": { # biggest model for 'Thematisierungsintensität', merged from several sources
        "path": "../data/models/mo10", #formerly t4__tdc100__s1_articles_tr5__s3_tr10__s4_tr10__s5_tr10__s6_tr10 , where sX means dataset and trX means TransformationRule
        "text_labels": "Thematisierungsintensität: TI: Hauptthema, TI: Nebenthema, TI: Verweis",
        "source": [(gold_data, "g1"), (gold_data, "g5"), (gold_data, "g6"), (gold_data, "g7"), (gold_data, "g8")],
        "trainer_class": Trainer4,
        "gold_data_transform_rule": [TransformRule5, TransformRule10, TransformRule10, TransformRule10, TransformRule10],
        "train_data_cutoff": 100,
        "iteration_limit": 20,
        "exclusive_classes": True,
        "train_data_size": 2803,
        "train_data_hash": 319029941,
        "eval_data_hash": 3211313,
        "spacy_version": "2.3",
    },
    "mo11": {
        "path": "../data/models/mo11",
        "text_labels": "Verantwortungsreferenz",
        "source": (gold_data, "g1"),
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule7,
        "train_data_cutoff": 100,
        "iteration_limit": 20,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_lg",
        "spacy_version": "2.3",
    },
    "mo12": {
        "path": "../data/models/mo12",
        "text_labels": "Verantwortungsreferenz",
        "source": (gold_data, "g1"),
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule7,
        "train_data_cutoff": 80,
        "iteration_limit": 20,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_lg",
        "spacy_version": "2.3",
    },
    "mo13": {
        "path": "../data/models/mo13", # im Log steht: ../data/models/t4__tdc100_i45__s1_articles_tr11/
        "text_labels": "Risikotyp", 
        "source": (gold_data, "g1"), # articles # TODO: check if this was really g1
        "trainer_class": Trainer4, 
        "gold_data_transform_rule": TransformRule11, 
        "train_data_cutoff": 100, 
        "train_data_length": 1499, 
        "train_data_hash": 311886498,
        "iteration_limit": 45, 
        "dropout": 0.2, 
        "exclusive_classes": False, 
        "spacy_base_model": "de_core_news_sm", 
        "spacy_version": "2.2.4", 
    }, 
    "mo14": {
        "path": "../data/models/mo14", # im Log steht: ../data/models/t4__tdc100_i2__s1_sentences_tr11/
        "text_labels": "Risikotyp", 
        "source": (gold_data, "g2"), # sentences # TODO: check if this was really g1
        "trainer_class": Trainer4, 
        "gold_data_transform_rule": TransformRule11, 
        "train_data_cutoff": 100, 
        "train_data_length": 60208, 
        "train_data_hash": "411566864", 
        "iteration_limit": 2, 
        "dropout": 0.2, 
        "exclusive_classes": False, 
        "spacy_base_model": "de_core_news_sm", 
        "spacy_version": "2.2.4", 
    },
    "mo15": {
        "path": "../data/models/mo15",
        "text_labels": "Tonalität: 'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1", "g5", "g6", "g7", "g8"),
        "trainer_class": Trainer4,
        "gold_data_transform_rule": (TransformRule3, TransformRule13, TransformRule13, TransformRule13, TransformRule13),
        "train_data_cutoff": 100,
        "train_data_length": "2323 texts",# The gold data contains 2803 texts, but 480 of them had no category assigned, so they were removed
        "train_data_hash": 310903462,
        "iteration_limit": 30,
        "dropout": 0.2,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_lg",
        "spacy_version": "2.3",
    },
    "mo16": {
        "path": "../data/models/mo16",
        "text_labels": "'V: Zuweisende Partei', 'V: Verantwortungssubjekt', 'V: Modi Verantwortungszuweisung', 'V: Zeitliche Dimension', und alle Subkategorien dazu",
        "source": (gold_data, "g1"),
        "trainer_class": Trainer4,
        "gold_data_transform_rule": (TransformRule16, TransformRule17),
        "train_data_cutoff": 100,
        "train_data_length": "1499 texts",# The gold data contains 2803 texts, but 480 of them had no category assigned, so they were removed
        "train_data_hash": None, # TODO final
        "iteration_limit": 40,
        "dropout": 0.2,
        "exclusive_classes": False,
        "spacy_base_model": "de_core_news_lg",
        "spacy_version": "2.3",
    },
}

model_indices = {
    # All of the following indices were done on corpus "amc_corpora['mara002']" with a nlp model
    "i1": {
        "table_name": "i1", #formerly part of index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5
        "col_names": "'AF: Social Companions', 'AF: Soziale Medien', and all other 31 AF",
        "source": (models, "mo3"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i2": {
        "table_name": "i2", #formerly part of index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5
        "col_names": "'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (models, "mo5"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i3": {
        "table_name": "i3", #formerly part of index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5
        "col_names": "TI: Hauptthema, TI: Nebenthema, TI: Verweis",
        "source": (models, "mo7"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i4": {
        "table_name": "i4", #formerly index_3__mara002__af
        "col_names": "AF: Social Companions, AF: Soziale Medien",
        "source": (models, "mo9"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i5": {
        "table_name": "i5", #formerly index_3__mara002__ti
        "col_names": "TI: Hauptthema, TI: Nebenthema, TI: Verweis",
        "source": (models, "mo10"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i6": {
        "table_name": "i6",
        "col_names": "Verantwortungsreferenz",
        "source": (models, "mo11"),
        "index_creation_logic": model_indexer.index_articles
    },
}

lmvr = {
    # TODO
}

evaluations = {
    # TODO
}

