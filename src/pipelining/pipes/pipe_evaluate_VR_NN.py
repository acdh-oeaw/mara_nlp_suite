from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main
from trainer.trainer4 import Trainer4

# We are evaluating mo11, which was trained on g1 (MAXQDA-corpus over articles), 
# against the annotations performed in p5 (VR: ja/nein). 
# p5 served texts in mara002 that contain a lot of/very rare/many different LM. 

# Caveat: 
# The annotators of p5 selected VR=ja only if the text was relevant (resp. if the VR in the text was relevant). 
# It may thus be necessary to only evaluate those texts where AF=SM or AF=SC. 
# Check back with the annotators (Christian Bauer) for more information on what exactly was annotated. 

class ConfigLoadG8(ConfigRoot):

    gold_data_json_path = data_flow_registry.gold_data["g8"]["path"] # annotated VR: ja/nein 
    gold_data_transform_rule = gold_data_transform_rules.TransformRule12 # remove non-VR; make VR an optional multi-label

class ConfigLoadVRModel(ConfigRoot): 

    should_load_model = True
    model_def_dict = data_flow_registry.models["mo11"] # trained over g1
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]

class ConfigLoadAFModel(ConfigRoot): 

    should_load_model = True 
    model_def_dict = data_flow_registry.models["mo9"] 
    trainer_class = model_def_dict["trainer_class"]
    model_path = model_def_dict["path"]

def run():

    eval_data_container = main.load_gold_data(ConfigLoadG8)
    eval_data_container = main.transform_gold_data(ConfigLoadG8, eval_data_container)

    modelVR = main.init_trainer(ConfigLoadVRModel)

    main.log_manager.info_global(
        "--------------------------------\n"
        "Evaluating mo11 over the entire dataset g8: \n"
    )
    scores_spacy, scores_manual = modelVR.evaluate(eval_data_container)

    # only look at those examples that mo9 predicts as either AF=SM or AF=SC
    modelAF = main.init_trainer(ConfigLoadAFModel)

    gdis_to_keep = []

    for gdi in eval_data_container.gold_data_item_list: 
    
        doc = modelAF.nlp(gdi.text)

        for cat in ['AF: Social Companions', 'AF: Soziale Medien']: 
            if doc.cats[cat] > 0.5: 
                gdis_to_keep.append(gdi)
                break 

    eval_data_container2 = GoldDataContainer()
    eval_data_container2.cats_list = eval_data_container.cats_list
    eval_data_container2.gold_data_item_list = gdis_to_keep

    main.log_manager.info_global(
        "--------------------------------\n"
        "Evaluating mo11 over those texts in g8 that mo9 predicts to be AF=SM or AF=SC: \n"
    )
    scores_spacy2, scores_manual2 = modelVR.evaluate(eval_data_container2)

    # only look at those examples that were annotated as AF=SM or AF=SC
    
    # we need to reload the data to undo the transformation that removes AF
    eval_data_container = main.load_gold_data(ConfigLoadG8)

    gdis_to_keep = [] 

    for gdi in eval_data_container.gold_data_item_list: 

        for cat in ['AF: Social Companions', 'AF: Soziale Medien']:
            if gdi.cats[cat] == 1:
                gdis_to_keep.append(gdi)
                break 

    eval_data_container3 = GoldDataContainer()
    eval_data_container3.cats_list = eval_data_container.cats_list
    eval_data_container3.gold_data_item_list = gdis_to_keep

    # now apply the transformation that removes all categories except VR
    eval_data_container3 = main.transform_gold_data(ConfigLoadG8, eval_data_container3) 

    main.log_manager.info_global(
        "--------------------------------\n"
        "Evaluating mo11 over those texts in g8 that were annotated as AF=SM or AF=SC: \n"
    )
    scores_spacy3, scores_manual3 = modelVR.evaluate(eval_data_container3)

    embed()
