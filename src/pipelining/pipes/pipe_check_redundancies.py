from etl.gold_data_manager import GoldDataContainer
from pipelining.pipe_root import ConfigRoot
from etl import maxqdata_manager, gold_data_transform_rules, gold_data_manager
from pipelining import data_flow_registry
from IPython import embed
import main




def run_2():

    class Config1_1(ConfigRoot):
        # g1 combined with tr2 produces gold data that was formerly persisted as 's1_articles__tr2_1__sc_sm_alle_anwendungsfelder.json'
        gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule2

    class Config1_2(ConfigRoot):
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config2(ConfigRoot):
        # formerly s2 in prodigy, now p1 in prodigy data, and persisted as gold data as g4
        gold_data_json_path = data_flow_registry.gold_data["g4"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule9

    class Config3(ConfigRoot):
        # formerly s3 in prodigy, now p2 in prodigy data, and persisted as gold data as g5
        gold_data_json_path = data_flow_registry.gold_data["g5"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config4(ConfigRoot):
        # formerly s4 in prodigy, now p3 in prodigy data, and persisted as gold data as g6
        gold_data_json_path = data_flow_registry.gold_data["g6"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config5(ConfigRoot):
        # formerly s5 in prodigy, now p4 in prodigy data, and persisted as gold data as g7
        gold_data_json_path = data_flow_registry.gold_data["g7"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config6(ConfigRoot):
        # formerly s6 in prodigy, now p5 in prodigy data, and persisted as gold data as g8
        gold_data_json_path = data_flow_registry.gold_data["g8"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    ConfigRoot.gold_data_json_path = "../data/gold_data/s1_articles__tr2_1__sc_sm_alle_anwendungsfelder_X.json"
    gdc_old = main.load_gold_data(ConfigRoot)

    gdc_1 = main.load_gold_data(Config1_1)
    gdc_1 = main.transform_gold_data(Config1_1, gdc_1)
    gdc_1 = main.transform_gold_data(Config1_2, gdc_1)
    gdc = GoldDataContainer(cats_list=gdc_1.cats_list)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_1)

    gdc_2 = main.load_gold_data(Config2)
    gdc_2 = main.transform_gold_data(Config2, gdc_2)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_2)

    gdc_3 = main.load_gold_data(Config3)
    gdc_3 = main.transform_gold_data(Config3, gdc_3)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_3)

    gdc_4 = main.load_gold_data(Config4)
    gdc_4 = main.transform_gold_data(Config4, gdc_4)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_4)

    gdc_5 = main.load_gold_data(Config5)
    gdc_5 = main.transform_gold_data(Config5, gdc_5)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_5)

    gdc_6 = main.load_gold_data(Config6)
    gdc_6 = main.transform_gold_data(Config6, gdc_6)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_6)

    gdc_new = gdc


    pair_differences = []

    for i, gdi_o in enumerate(gdc_old.gold_data_item_list):

        found = False

        for gdi_n in gdc_new.gold_data_item_list:

            if gdi_o.article_id == gdi_n.article_id:

                if gdi_o.cats != gdi_n.cats:
                    texts_equal = gdi_o.text == gdi_n.text
                    pair_differences.append({"gdi_o": gdi_o, "gdi_n": gdi_n})
                else:
                    print(i)

                found = True
                break

        if not found:
            print(i)

    gdc_d = GoldDataContainer(cats_list=gdc.cats_list)
    for p in pair_differences:
        gdc_d.gold_data_item_list.append(p["gdi_o"])
        gdc_d.gold_data_item_list.append(p["gdi_n"])

    ConfigRoot.gold_data_json_path = "../data/gold_data/differences.json"
    main.persist_gold_data(ConfigRoot, gdc_d)

    embed()


def run_3():

    ConfigRoot.gold_data_json_path = "../data/gold_data/differences.json"
    gdc = main.load_gold_data(ConfigRoot)
    print()

def run_4():

    class C1(ConfigRoot):
        gold_data_json_path = "../data/gold_data/g1.json"

    class C2(ConfigRoot):
        gold_data_json_path = "../data/gold_data/s1_articles__tr2_1__sc_sm_alle_anwendungsfelder_ORIGINAL.json"

    class C3(ConfigRoot):
        gold_data_json_path = "../data/gold_data/differences.json"

    gdc1 = main.load_gold_data(C1)
    gdc2 = main.load_gold_data(C2)
    gdc3 = main.load_gold_data(C3)

    a = None
    for gdi in gdc1.gold_data_item_list:
        if gdi.article_id == "STANDARD_200203161928100152":
            if a is not None:
                raise Exception()
            a = gdi

    b = None
    for gdi in gdc1.gold_data_item_list:
        if gdi.article_id == "STANDARD_200203161928100152":
            if b is not None:
                raise Exception()
            b = gdi


    class C4(ConfigRoot):
        gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule2

    class C5(ConfigRoot):
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    gdc4 = main.load_gold_data(C4)

    id = None
    for i, gdi in enumerate(gdc4.gold_data_item_list):
        if gdi.article_id == "STANDARD_200203161928100152":
            if id is not None:
                raise Exception()
            id = i
    del gdc4.gold_data_item_list[0:id]
    del gdc4.gold_data_item_list[1:]


    gdc4 = main.transform_gold_data(C4, gdc4)
    gdc4 = main.transform_gold_data(C5, gdc4)

    print()


def run_5():

    class C1(ConfigRoot):
        gold_data_json_path = "../data/gold_data/g1.json"

    class C2(ConfigRoot):
        gold_data_json_path = "../data/gold_data/s1_articles__tr2_1__sc_sm_alle_anwendungsfelder_ORIGINAL.json"

    gdc_n = main.load_gold_data(C1)
    gdc_o = main.load_gold_data(C2)

    ConfigRoot.gold_data_json_path = "../data/gold_data/s1_articles__tr2_1__sc_sm_alle_anwendungsfelder_X.json"
    gdc_o_X = main.load_gold_data(ConfigRoot)

    def reduce_gdc(gdc):

        # id = None
        multiples = []
        for i, gdi in enumerate(gdc.gold_data_item_list):
            if gdi.article_id == "STANDARD_200203161928100152":
                multiples.append(gdi)
                # if id is not None:
                #     raise Exception()
                # id = i
        del gdc.gold_data_item_list[0:id]
        # del gdc.gold_data_item_list[1:]

    # reduce_gdc(gdc_n)
    # reduce_gdc(gdc_o)
    reduce_gdc(gdc_o_X)

    class C3(ConfigRoot):
        gold_data_transform_rule = gold_data_transform_rules.TransformRule2

    class C4(ConfigRoot):
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    gdc_n = main.transform_gold_data(C3, gdc_n)
    gdc_n = main.transform_gold_data(C4, gdc_n)

    gdc_o = main.transform_gold_data(C4, gdc_o)

    print()


def get_redundancies_by_id(gdc: GoldDataContainer):

    ids_dict = {}
    redundant_ids_dict = {}

    for gdi in gdc.gold_data_item_list:

        if gdi.article_id in ids_dict:
            ids_dict[gdi.article_id].append(gdi)
            redundant_ids_dict[gdi.article_id] = ids_dict[gdi.article_id]
        else:
            ids_dict[gdi.article_id] = [gdi]

    return redundant_ids_dict


def run():

    class Config1_1(ConfigRoot):
        # g1 combined with tr2 produces gold data that was formerly persisted as 's1_articles__tr2_1__sc_sm_alle_anwendungsfelder.json'
        gold_data_json_path = data_flow_registry.gold_data["g1"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule2

    class Config1_2(ConfigRoot):
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config2(ConfigRoot):
        # formerly s2 in prodigy, now p1 in prodigy data, and persisted as gold data as g4
        gold_data_json_path = data_flow_registry.gold_data["g4"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule9

    class Config3(ConfigRoot):
        # formerly s3 in prodigy, now p2 in prodigy data, and persisted as gold data as g5
        gold_data_json_path = data_flow_registry.gold_data["g5"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config4(ConfigRoot):
        # formerly s4 in prodigy, now p3 in prodigy data, and persisted as gold data as g6
        gold_data_json_path = data_flow_registry.gold_data["g6"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config5(ConfigRoot):
        # formerly s5 in prodigy, now p4 in prodigy data, and persisted as gold data as g7
        gold_data_json_path = data_flow_registry.gold_data["g7"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    class Config6(ConfigRoot):
        # formerly s6 in prodigy, now p5 in prodigy data, and persisted as gold data as g8
        gold_data_json_path = data_flow_registry.gold_data["g8"]["path"]
        gold_data_transform_rule = gold_data_transform_rules.TransformRule8

    ConfigRoot.gold_data_json_path = "../data/gold_data/s1_articles__tr2_1__sc_sm_alle_anwendungsfelder_X.json"
    gdc_old = main.load_gold_data(ConfigRoot)

    gdc_1 = main.load_gold_data(Config1_1)
    gdc_1 = main.transform_gold_data(Config1_1, gdc_1)
    gdc_1 = main.transform_gold_data(Config1_2, gdc_1)
    for gdi in gdc_1.gold_data_item_list:
        gdi.source = "g1" # TODO: Damit dass geht muss golddataitem und gold_data_manager angepasst werden

    gdc = GoldDataContainer(cats_list=gdc_1.cats_list)
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_1)

    gdc_2 = main.load_gold_data(Config2)
    gdc_2 = main.transform_gold_data(Config2, gdc_2)
    for gdi in gdc_2.gold_data_item_list:
        gdi.source = "g4"
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_2)

    gdc_3 = main.load_gold_data(Config3)
    gdc_3 = main.transform_gold_data(Config3, gdc_3)
    for gdi in gdc_3.gold_data_item_list:
        gdi.source = "g5"
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_3)

    gdc_4 = main.load_gold_data(Config4)
    gdc_4 = main.transform_gold_data(Config4, gdc_4)
    for gdi in gdc_4.gold_data_item_list:
        gdi.source = "g6"
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_4)

    gdc_5 = main.load_gold_data(Config5)
    gdc_5 = main.transform_gold_data(Config5, gdc_5)
    for gdi in gdc_5.gold_data_item_list:
        gdi.source = "g7"
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_5)

    gdc_6 = main.load_gold_data(Config6)
    gdc_6 = main.transform_gold_data(Config6, gdc_6)
    for gdi in gdc_6.gold_data_item_list:
        gdi.source = "g8"
    gdc = gold_data_manager.merge_assuming_identical_categories(gdc, gdc_6)

    get_redundancies_by_id(gdc)