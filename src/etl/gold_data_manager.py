from __future__ import annotations
import json
import random
from loggers import log_manager
from etl.gold_data_transform_rules import TransformRule
from typing import List, Dict, Set, Tuple, Generator, Type


class GoldDataItem:

    article_id: str
    text: str
    cats: Dict[str, int]
    __slots__ = ["article_id", "text", "cats"]

    def __init__(self, article_id=None, text=None, cats=None):

        self.article_id = article_id
        self.text = text
        self.cats = cats


    def get_in_spacy_format(self) -> Tuple[str, Dict[str, Dict]]:

        return (self.text, {"cats": self.cats})


    def copy(self):

        return GoldDataItem(
            article_id=self.article_id,
            text=self.text,
            cats=self.cats.copy()
        )


class GoldDataContainer:

    # TODO : Should it be needed, implement recursive cats_hierarchy here
    cats_list: List[str]
    gold_data_item_list: List[GoldDataItem]
    __slots__ = ["cats_list", "gold_data_item_list"]

    def __init__(self, cats_list=None, gold_data_item_list=None):

        self.cats_list = [] if cats_list is None else cats_list
        self.gold_data_item_list = [] if gold_data_item_list is None else gold_data_item_list


    def get_in_spacy_format(self) -> Generator[Tuple[str, Dict[str, Dict]]]:

        for gdi in self.gold_data_item_list:

            yield gdi.get_in_spacy_format()


    def copy(self):

        gdc_copy = GoldDataContainer()
        gdc_copy.cats_list = self.cats_list.copy()
        gdc_copy.gold_data_item_list = [gdi.copy() for gdi in self.gold_data_item_list]

        return gdc_copy

    def remove_cats_without_assignments(self):

        indices_to_remove = []
        for i, gdi in enumerate(self.gold_data_item_list):
            found = False
            for val in gdi.cats.values():
                if val == 1:
                    found = True
            if not found:
                indices_to_remove.append(i)
        for i in indices_to_remove[-1::-1]:
            del self.gold_data_item_list[i]

        return self
    


def export_to_dict(gold_data_container: GoldDataContainer) -> Dict:

    cats_list = gold_data_container.cats_list
    cats_list.sort()

    return {
        "cats_list": cats_list,
        "gold_data_item_list": [
            {
                "article_id": gdi.article_id,
                "text": gdi.text,
                "cats": [gdi.cats[c] for c in cats_list],
                # "cats": gdi.cats,
            }
            for gdi in gold_data_container.gold_data_item_list
        ]
    }


def import_from_dict(data_dict: Dict) -> GoldDataContainer:

    gold_data_container = GoldDataContainer()

    gold_data_container.cats_list = data_dict["cats_list"]

    for data_item in data_dict["gold_data_item_list"]:

        data_item: Dict

        gold_data_container.gold_data_item_list.append(
            GoldDataItem(
                article_id=data_item["article_id"],
                text=data_item["text"],
                cats={
                    cat: assigned
                    for cat, assigned in
                    zip(data_dict["cats_list"], data_item["cats"])
                }
            )
        )

        if len(data_item.keys()) != len(GoldDataItem.__slots__):

            raise Exception("Length differences found between dictionary objet and GoldDataItem.")

    return gold_data_container


def load_from_json(gold_data_json_path: str) -> GoldDataContainer:

    with open(gold_data_json_path) as f:

        data_all_dict = json.load(f)

        return import_from_dict(data_all_dict)


def transform_cats(
    gold_data_transform_rule: Type[TransformRule],
    gold_data_container: GoldDataContainer
) -> GoldDataContainer:


    # Replace the cats_list overview of gold_data_container

    cats_list_new = []

    for cat_old, cat_new in gold_data_transform_rule.cat_replacements:

        if cat_new not in cats_list_new:

            found_old = False

            for cat_old_assigned in gold_data_container.cats_list:

                if cat_old_assigned == cat_old:

                    found_old = True
                    cats_list_new.append(cat_new)

            if not found_old:

                log_manager.info_global(
                    f"Did not find Occurence of category to be replaced: '{cat_old}'\n"
                    "It could be the case that no text got assigned to this category and it was filtered out.\n"
                    "If so, ignore this warning."
                )

    gold_data_container.cats_list = cats_list_new


    # Replace the assigned cats to each gold_data_item

    for gold_data_item in gold_data_container.gold_data_item_list:

        gold_data_item: GoldDataItem
        cats_dict_old = gold_data_item.cats
        cats_dict_new = {}

        for cat_old, cat_new in gold_data_transform_rule.cat_replacements:

            if cat_old in cats_dict_old:

                if cats_dict_old[cat_old] == 1:

                    cats_dict_new[cat_new] = 1

                elif cats_dict_old[cat_old] == 0 and cat_new not in cats_dict_new:

                    cats_dict_new[cat_new] = 0

        if len(cats_dict_new.keys()) == 0:

            raise Exception("Not a single transformation was done. This can't be on purpose?")

        gold_data_item.cats = cats_dict_new


    return gold_data_container


def persist_to_json(gold_data_json_path: str, gold_data_container: GoldDataContainer):

    gold_data_json_dict = export_to_dict(gold_data_container=gold_data_container)

    with open(gold_data_json_path, "w", encoding="utf8") as f:

        # makes the json more readable but roughly 2x bigger when it contains only sentences
        # json.dump(gold_data_json_dict, f, indent=2, ensure_ascii=False)
        json.dump(gold_data_json_dict, f, ensure_ascii=False)

    log_manager.info_global(f"Persisted to file: {gold_data_json_path}")


def split_into_train_eval_data(
    gold_data_container: GoldDataContainer,
    data_cutoff: int
) -> Tuple[GoldDataContainer, GoldDataContainer]:

    random.seed(42)
    gold_data_container = gold_data_container.copy()
    random.shuffle(gold_data_container.gold_data_item_list)

    pos = round(len(gold_data_container.gold_data_item_list) * data_cutoff / 100)

    train_data_container = GoldDataContainer(
        cats_list=gold_data_container.cats_list,
        gold_data_item_list=gold_data_container.gold_data_item_list[:pos]
    )
    eval_data_container = GoldDataContainer(
        cats_list=gold_data_container.cats_list,
        gold_data_item_list=gold_data_container.gold_data_item_list[pos:]
    )

    return train_data_container, eval_data_container


def merge_assuming_identical_categories(gdc1: GoldDataContainer, gdc2: GoldDataContainer) -> GoldDataContainer:

    if gdc1.cats_list == [] and gdc2.cats_list == []:
        return None

    elif gdc1.cats_list == [] and gdc2.cats_list != []:
        gdc = GoldDataContainer(cats_list=gdc2.cats_list)

    elif gdc1.cats_list != [] and gdc2.cats_list == []:
        gdc = GoldDataContainer(cats_list=gdc1.cats_list)

    elif gdc1.cats_list != [] and gdc2.cats_list != []:
        assert gdc1.cats_list == gdc2.cats_list
        gdc = GoldDataContainer(cats_list=gdc1.cats_list)

    gdc.gold_data_item_list = gdc1.gold_data_item_list + gdc2.gold_data_item_list

    return gdc


def extend_with_additional_cats(gdc_1, gdc_2):
    
    gdc_merged = GoldDataContainer()
    gdc_merged.cats_list = gdc_1.cats_list + gdc_2.cats_list
    gdc_merged.gold_data_item_list = []

    for gdi_1, gdi_2 in zip(gdc_1.gold_data_item_list, gdc_2.gold_data_item_list):
        if gdi_1.article_id != gdi_2.article_id or gdi_1.text != gdi_2.text:
            raise Exception()
        else:
            cats_merged = {}
            cats_merged.update(gdi_1.cats)
            cats_merged.update(gdi_2.cats)

            gdc_merged.gold_data_item_list.append(
                GoldDataItem(
                    article_id=gdi_1.article_id,
                    text=gdi_1.text,
                    cats=cats_merged
                )
            )

    return gdc_merged


def reduce_to_overlap(gdc_1: GoldDataContainer, gdc_2: GoldDataContainer):

    def remove_from_a(gdc_a: GoldDataContainer, gdc_b: GoldDataContainer):

        i_to_remove = []
        for i, c in enumerate(gdc_a.cats_list):
            if c not in gdc_b.cats_list:
                i_to_remove.append(i)
        for i in i_to_remove[-1::-1]:
            cat = gdc_a.cats_list[i]
            for gdi in gdc_a.gold_data_item_list:
                del gdi.cats[cat]
            del gdc_a.cats_list[i]

        return gdc_a

    gdc_1 = remove_from_a(gdc_a=gdc_1, gdc_b=gdc_2)
    gdc_2 = remove_from_a(gdc_a=gdc_2, gdc_b=gdc_1)

    def verify(gdc_1: GoldDataContainer, gdc_2: GoldDataContainer):

        if gdc_1.cats_list != gdc_2.cats_list:
            raise Exception

        for gdi_1 in gdc_1.gold_data_item_list:
            for gdi_2 in gdc_2.gold_data_item_list:
                if gdi_1.cats.keys() != gdi_2.cats.keys():
                    raise Exception

    return gdc_1, gdc_2