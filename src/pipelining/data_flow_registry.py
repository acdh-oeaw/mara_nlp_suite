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
    "md2": { # Probecodierung mit 50 Texten
    },
    "md3_SC": { # Vertiefungsanalyse SC
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-12-17/101_derived/mara_SocialCompanions/",
        "annotations_xlsx_file_path": "../data/maxqdata_data/annotations_maxqdata/2021 Vertiefungsanalyse/2021-03-04 Codierung_SC_27022021.mx20.xlsx", # vollständige Rohfassung
        "source": (models, ""), # TODO which models / indices were used?
        "source_selection_logic": "'AF: Social Companions' between 0.99983 and 0.505869, 'TI: Hauptthema' between 1.00000 and 0.562652, LMVR-logic" # see redmine ticket #99471
    },
    "md3_SM": { # Vertiefungsanalyse SM
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-12-17/101_derived/mara_SozialeMedien/",
        "annotations_xlsx_file_path": None,
        "source": (models, ""), # TODO which models / indices were used?
        "source_selection_logic": "'AF: Soziale Medien' between 0.999896 and 0.72494, 'TI: Hauptthema' between 1.000000 and 0.515524, LMVR-logic" # see redmine ticket #99471
    },
    "md3_SMSC": { # Vertiefungsanalyse von Texten, die sowohl als SM als auch SC predicted sind
        "articles_xml_directory": "../data/maxqdata_data/amc_subcorpus/2020-12-17/101_derived/mara_SozialeMedien_SocialCompanions/",
        "annotations_xlsx_file_path": None,
        "source": (models, ""), # TODO which models / indices were used?
        "source_selection_logic": "'AF: Soziale Medien' and 'AF: Social Companions' above 0.9, 'TI: Hauptthema' between 1.0 and 0.991806, LMVR-logic" # see redmine ticket #99471
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
        "source_selection_logic": "sort by SC+SM desc", # TODO: Fetch logic from git history, re-integrate it into current code so that it can be referenced here and re-run.
        "size": "412 articles",
    },
    "p3": {
        "dataset_name": "p3", #formerly s4
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität",
        "source": (model_indices, ["i1", "i2", "i3"]),
        "source_selection_logic": "sort by SM desc", # TODO: Fetch logic from git history, re-integrate it into current code so that it can be referenced here and re-run.
        "size": "202 articles",
    },
    "p4": {
        "dataset_name": "p4", #formerly s5
        "text_labels": "Anwendungsfelder (SC,SM,Alle anderen einzeln), Tonalität, Thematisierungsintensität, 'af_sc_sm'", # TODO: In the prodigy dataset is an additional label 'af_sc_sm'; investigate
        "source": (model_indices, ["i1", "i2", "i3"]),
        "source_selection_logic": "sort by SC+SM asc", # TODO: Fetch logic from git history, re-integrate it into current code so that it can be referenced here and re-run.
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
}

models = {
    "mo1": {
        "path": "../data/models/mo1", #TODO : Fetch from git history
        "text_labels": "'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
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
    "mo1_1": {
        "path": "../data/models/mo1_1",
        "text_labels": "'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule1,
        "train_data_cutoff": 100,
        "iteration_limit": 40,
        "exclusive_classes": False,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo1_2": {
        "path": "../data/models/mo1_2",
        "text_labels": "'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule1,
        "train_data_cutoff": 100,
        "iteration_limit": 40,
        "exclusive_classes": False,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo2": {
        "path": "../data/models/mo2", #TODO : Fetch from git history
        "text_labels": "'Social Companions', 'Soziale Medien', 'Andere Anwendungsfelder'",
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
        "text_labels": "'AF: Social Companions', 'AF: Soziale Medien', and all other 31 AF",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule2,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": False,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo4": {
        "path": "../data/models/mo4", #formerly t4__tdc50__s1_articles__tr2_1__sc_sm_alle_anwendungsfelder or t4__tdc50__s1__tr2_1__sc_sm_alle_anwendungsfelder
        "text_labels": "'AF: Social Companions', 'AF: Soziale Medien', and all other 31 AF",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule2,
        "train_data_cutoff": 50,
        "iteration_limit": 30,
        "exclusive_classes": False,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo5": {
        "path": "../data/models/mo5", #formerly t4__tdc100__s1_articles__tr3__tonalitaet or t4__tdc100__s1__tr3__tonalitaet
        "text_labels": "'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule3,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo5_1": { # TODO: Delete once not needed anymore. This is a duplicated model of mo5 to check for inconsistencies
        "path": "../data/models/mo5_1",
        "text_labels": "'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule3,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo5_2": { # TODO: Delete once not needed anymore. This is a duplicated model of mo5 to check for inconsistencies
        "path": "../data/models/mo5_2",
        "text_labels": "'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule3,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo6": {
        "path": "../data/models/mo6", #formerly t4__tdc50__s1_articles__tr3__tonalitaet or t4__tdc50__s1__tr3__tonalitaet
        "text_labels": "'T: negativ', 'T: ambivalent', 'T: positiv', 'T: keine Tonalität ggü. KI, Algorithmen, Automatisierung'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule3,
        "train_data_cutoff": 50,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo7": {
        "path": "../data/models/mo7", #formerly t4__tdc100__s1_articles__tr5__thematisierungsintensitaet or t4__tdc100__s1__tr5__thematisierungsintensitaet
        "text_labels": "'TI: Hauptthema', 'TI: Nebenthema', 'TI: Verweis'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule5,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo7_1": { # TODO: Delete once not needed anymore. This is a duplicated model of mo7 to check for inconsistencies
        "path": "../data/models/mo7_1",
        "text_labels": "'TI: Hauptthema', 'TI: Nebenthema', 'TI: Verweis'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule5,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo7_2": { # TODO: Delete once not needed anymore. This is a duplicated model of mo7 to check for inconsistencies
        "path": "../data/models/mo7_2",
        "text_labels": "'TI: Hauptthema', 'TI: Nebenthema', 'TI: Verweis'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule5,
        "train_data_cutoff": 100,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
    },
    "mo8": {
        "path": "../data/models/mo8", #formerly t4__tdc50__s1_articles__tr5__thematisierungsintensitaet or t4__tdc50__s1__tr5__thematisierungsintensitaet
        "text_labels": "'TI: Hauptthema', 'TI: Nebenthema', 'TI: Verweis'",
        "source": (gold_data, "g1"), # minus 28 misformed texts
        "trainer_class": Trainer4,
        "gold_data_transform_rule": TransformRule5,
        "train_data_cutoff": 50,
        "iteration_limit": 30,
        "exclusive_classes": True,
        "spacy_base_model": "de_core_news_sm",
        "spacy_version": "2.2.4",
        # TODO: Add train_data_size, train_data_hash, eval_data_hash
    },
    "mo9": {
        "path": "../data/models/mo9", #retrained with (supposedly) equivalent parameters as t4__tdc100__s1_articles_tr2_1_tr8__s2_tr9__s3_tr8__s4_tr8__s5_tr8__s6_tr8
        "text_labels": "'AF: Social Companions', 'AF: Soziale Medien'",
        "source": [(gold_data, "g1"), (gold_data, "g4"), (gold_data, "g5"), (gold_data, "g6"), (gold_data, "g7"), (gold_data, "g8")],
        "trainer_class": Trainer4,
        "gold_data_transform_rule": [(TransformRule2, TransformRule8), TransformRule9, TransformRule8, TransformRule8, TransformRule8, TransformRule8],
        "train_data_cutoff": 100,
        "iteration_limit": 20,
        "exclusive_classes": False,
        "train_data_size": 3105,
        "train_data_hash": 312607402,
        "eval_data_hash": 3211313,
        "spacy_base_model": None, # TODO
        "spacy_version": "2.3",
    },
    "mo10": { # TODO: re-train this
        "path": "../data/models/mo10", #retrained with (supposedly) equivalent parameters as t4__tdc100__s1_articles_tr5__s3_tr10__s4_tr10__s5_tr10__s6_tr10
        "text_labels": None, #TODO
        "source": None, #TODO
        "trainer_class": Trainer4,
        "gold_data_transform_rule": None, #TODO
        "train_data_cutoff": 100,
        "iteration_limit": 20,
        "exclusive_classes": True,
        "spacy_base_model": None, # TODO
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
        "source": (gold_data, "g1"), # articles
        "trainer_class": Trainer4, 
        "gold_data_transform_rule": TransformRule11, 
        "train_data_cutoff": 100, 
        "train_data_length": 1499, 
        "train_data_hash": "311886498", 
        "iteration_limit": 45, 
        "dropout": 0.2, 
        "exclusive_classes": False, 
        "spacy_base_model": "de_core_news_sm", 
        "spacy_version": "2.2.4", 
    }, 
    "mo14": {
        "path": "../data/models/mo14", # im Log steht: ../data/models/t4__tdc100_i2__s1_sentences_tr11/
        "text_labels": "Risikotyp", 
        "source": (gold_data, "g2"), # sentences
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
    }
}

model_indices = {
    # All of the following indices were done on corpus "amc_corpora['mara002']" with a nlp model
    "i1": {
        "table_name": "i1", #formerly part of index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5
        "col_names": ((models, "mo3"), "text_labels"),
        "source": (models, "mo3"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i2": {
        "table_name": "i2", #formerly part of index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5
        "col_names": ((models, "mo5"), "text_labels"),
        "source": (models, "mo5"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i3": {
        "table_name": "i3", #formerly part of index_1__mara002__t4__tdc100__s1__tr2_1_tr3_tr5
        "col_names": ((models, "mo7"), "text_labels"),
        "source": (models, "mo7"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i4": {
        "table_name": "i4", #formerly index_3__mara002__af
        "col_names": ((models, "mo9"), "text_labels"),
        "source": (models, "mo9"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i5": {
        "table_name": "i5", #formerly index_3__mara002__ti
        "col_names": ((models, "mo10"), "text_labels"),
        "source": (models, "mo10"),
        "index_creation_logic": model_indexer.index_articles
    },
    "i6": {
        "table_name": "i6",
        "col_names": ((models, "mo11"), "text_labels"),
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

model_compare_indices = {
    "mci1_1": {
        "table_name": "mci1_1",
        "col_names": ((models, "mo5_1"), "text_labels"),
        "source": (models, "mo5_1"), # Not commited since this is redundant model for local testing
        "index_creation_logic": model_indexer.index_articles
    },
    "mci1_2": {
        "table_name": "mci1_2",
        "col_names": ((models, "mo5_2"), "text_labels"),
        "source": (models, "mo5_2"), # Not commited since this is redundant model for local testing
        "index_creation_logic": model_indexer.index_articles
    },
    "mci2_1": {
        "table_name": "mci2_1",
        "col_names": ((models, "mo7_1"), "text_labels"),
        "source": (models, "mo7_1"), # Not commited since this is redundant model for local testing
        "index_creation_logic": model_indexer.index_articles
    },
    "mci2_2": {
        "table_name": "mci2_2",
        "col_names": ((models, "mo7_2"), "text_labels"),
        "source": (models, "mo7_2"), # Not commited since this is redundant model for local testing
        "index_creation_logic": model_indexer.index_articles
    },
    "mci3_1": {
        "table_name": "mci3_1",
        "col_names": ((models, "mo1_1"), "text_labels"),
        "source": (models, "mo1_1"), # Not commited since this is redundant model for local testing
        "index_creation_logic": model_indexer.index_articles
    },
    "mci3_2": {
        "table_name": "mci3_2",
        "col_names": ((models, "mo1_2"), "text_labels"),
        "source": (models, "mo1_2"), # Not commited since this is redundant model for local testing
        "index_creation_logic": model_indexer.index_articles
    },
}