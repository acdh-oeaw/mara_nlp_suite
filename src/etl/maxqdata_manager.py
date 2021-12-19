import json
from collections import OrderedDict
import pandas as pd
import csv
import sys
import spacy
import os
import random
import re
import xml.etree.ElementTree as ET
from typing import List, Set
from _datetime import datetime
from loggers import log_manager
from etl.gold_data_manager import GoldDataContainer, GoldDataItem

# TODO : Implement python type hints in all functions

class CodingNode:
    """
    Class encapsulating the codings / annotations done by the annotators.

    ** attributes of main interest **
    children: returns all children coding nodes of the current node, use children on children to traverse the whole tree.
    article_annotated_set: returns a set of all ArticleAnnotated objects the current coding node has annotations on.

    ** other attributes **
    parent
    coding_value
    anzahl_codings
    anzahl_dokumente
    """

    def __init__(self, coding_value, parent=None, anzahl_codings=None, anzahl_dokumente=None, article_annotated_set=None):

        self.coding_value = coding_value
        self.parent = parent
        self.anzahl_codings = anzahl_codings
        self.anzahl_dokumente = anzahl_dokumente
        self.children = []
        if article_annotated_set is None:
            self.article_annotated_set = set()
        # SpecialPathCase : BEGIN dirty work-around
        self.coding_path = None
        # SpecialPathCase : END

    def __str__(self):

        return "<CodingNode: '" + self.coding_value + "'>"


    def __repr__(self):

        return self.__str__()


    def get_all_subnodes(self):

        l = [self]
        for c in self.children:
            l.extend(c.get_all_subnodes())
        return l


    def get_hierarchy_path_as_str(self):

        if self.parent is not None:

            return self.parent.coding_value + "\\" + self.coding_value

        else:

            return self.coding_value


    def get_hierarchy_path_as_list(self):

        if self.parent is not None:

            parent_path = self.parent.get_hierarchy_path_as_list()

            return parent_path + [self]

        else:

            return [self]




class ArticleAnnotated:
    """
    Class encapsulating articles with all meta-data and codings / annotations attached.

    ** attributes of main interest **
    coding_list: returns all codings annotations of the article as a list of dictionaries
    field_inhalt: returns the string content of the article xml <field name="inhalt"> node

    ** other attributes **
    article_file_name
    id
    datum_full
    datum
    bibl
    docsrc_name
    region
    mediatype
    tokens
    ressort2
    docsrc
    field_titel
    field_stichwort
    article_file_content
    root_coding_node
    keys
    dupl_ftitle
    deskriptor
    autor
    mutation
    """

    def __init__(
            self,
            article_file_name,
            id=None,
            field_inhalt=None,
            datum_full=None,
            datum=None,
            bibl=None,
            docsrc_name=None,
            region=None,
            mediatype=None,
            tokens=None,
            ressort2=None,
            docsrc=None,
            field_titel=None,
            field_stichwort=None,
            article_file_content=None,
            article_file_content_cleaned=None,
            root_coding_node=None,
            keys=None,
            dupl_ftitle=None,
            deskriptor=None,
            autor=None,
            mutation=None,
            cats_dict=None,
    ):
        self.article_file_name = article_file_name
        self.article_id = id # the incoming param has to be id because that's how it is being passed from xml attributes
        self.datum_full = datetime.strptime(datum_full, "%Y-%m-%dT%H:%M:%SZ") if datum_full is not None else None
        self.datum = datum
        self.bibl = bibl
        self.docsrc_name = docsrc_name
        self.region = region
        self.mediatype = mediatype
        self.tokens = int(tokens) if tokens is not None else None
        self.ressort2 = ressort2
        self.docsrc = docsrc
        self.field_titel = field_titel
        self.field_stichwort = field_stichwort
        self.field_inhalt = field_inhalt
        self.article_file_content = article_file_content
        self.article_file_content_cleaned = article_file_content_cleaned
        self.root_coding_node = root_coding_node
        self.keys = keys
        self.dupl_ftitle = dupl_ftitle
        self.deskriptor = deskriptor
        self.autor = autor
        self.mutation = mutation
        self.cats_dict = cats_dict
        self.coding_list = []

        if article_file_content is not None:
            self.count_empty_lines_in_file_content()


    def __str__(self):
        return "<ArticleAnnotated: '" + self.article_id + "'>"


    def __repr__(self):
        return self.__str__()


    def __hash__(self):
        return hash(self.article_file_name)

    def __eq__(self, other):
        return self.article_file_name == other.article_file_name


    def count_empty_lines_in_file_content(self):

        self.empty_line_number_list = []

        for line_number, line in enumerate(self.article_file_content.splitlines()):

            if \
                    line == "" or \
                    line.isspace() or \
                    line == "\n" or \
                    line == "</p>":

                self.empty_line_number_list.append(line_number + 1)


    def correct_anfang_ende(self, anfang, ende, segment_for_check):

        corrected_anfang = anfang
        corrected_ende = ende

        for empty_line_number in self.empty_line_number_list:

            if corrected_anfang >= empty_line_number:
                corrected_anfang += 1

            if corrected_ende >= empty_line_number:
                corrected_ende += 1

            if corrected_anfang < empty_line_number and corrected_ende < empty_line_number:
                break

        segment_lines = segment_for_check.splitlines()
        article_lines = self.article_file_content.splitlines()

        if (
            (
                segment_lines[0] not in article_lines[corrected_anfang-1]
                or segment_lines[-1] not in article_lines[corrected_ende-1]
            )
            and (
                'fieldname="inhalt"' not in segment_lines[0]
                and 'fieldname="inhalt"' not in segment_lines[-1]
            )
        ):

            log_manager.info_global(f"Correcting the Anfang and Ende did not work correctly. Can be ignored most likely. article_id: {self.article_id}")

        return corrected_anfang, corrected_ende


    def add_coding(self, coding_anfang, coding_ende, coding_tag, coding_segment):

        def match_coding(coding_list, coding_node):

            for children_node in coding_node.children:

                if children_node.coding_value == coding_list[0]:

                    if len(coding_list) > 1:

                        return match_coding(coding_list[1:], children_node)

                    else:

                        children_node.article_annotated_set.add(self)
                        return children_node

            raise Exception("Could not find matching coding_node!")


        # SpecialPathCase : dirty work-around (see other comment on this)
        # uncomment the following lines to revert to the classical parsing
        #
        # codings_split = coding_tag.split("\\")
        # matching_coding_node = match_coding(codings_split, self.root_coding_node)
        # if codings_split[-1] != matching_coding_node.coding_value:
        #     raise Exception("Did not find correct matching coding_node")
        #
        # SpecialPathCase : BEGIN
        matching_coding_node = None

        for node in self.root_coding_node.get_all_subnodes():

            if node.coding_path.replace("Codesystem\\", "") == coding_tag:

                matching_coding_node = node
                node.article_annotated_set.add(self)

        if matching_coding_node is None:
            raise Exception()

        # SpecialPathCase : END

        coding_dict = {
            "coding_anfang": coding_anfang,
            "coding_ende": coding_ende,
            "coding_tag": coding_tag,
            "Segment": coding_segment,
            "coding_node": matching_coding_node,
        }

        found_coding_dict = False

        for existing_coding_dict in self.coding_list:

            if coding_dict == existing_coding_dict:

                found_coding_dict = True
                log_manager.info_global(f"Redundant coding found. Can be ignored most likely. article_id: {self.article_id}, coding_dict: {coding_dict} of ")

        if not found_coding_dict:

            self.coding_list.append(coding_dict)


    def get_in_spacy_format(self):

        return (self.field_inhalt, self.cats_dict)




def load_from_amc_and_maxqdata(annotations_xlsx_file_path, articles_xml_directory, limit_percent_data=100):

    def main():

        root_coding_node = generate_coding_nodes(annotations_xlsx_file_path)

        all_article_annotated_dict, count_successful_xml_parsing, count_not_successful_xml_parsing = parse_xml_articles(
            articles_xml_directory=articles_xml_directory,
            root_coding_node=root_coding_node,
            limit_percent_data=limit_percent_data
        )

        count_sucessful_coding_extraction, count_not_sucessful_coding_extraction = connect_codings_with_articles(
            annotations_xlsx_file_path=annotations_xlsx_file_path,
            article_annotated_dict=all_article_annotated_dict,
            root_coding_node=root_coding_node
        )

        log_manager.info_global(
            "\n" +
            "\nNumber of xml files succesfully parsed and transformed: " + str(count_successful_xml_parsing) +
            "\nNumber of xml files not parsed: " + str(count_not_successful_xml_parsing) +
            "\nAll files' contents were saved regardless of successful xml parsing or not."
            "The xml parsing is done only for extracting correct meta data."
            "\n" +
            "\nNumber of codings succesfully integrated into articles: " + str(count_sucessful_coding_extraction) +
            "\nNumber of codings not integrated: " + str(count_not_sucessful_coding_extraction) +
            "\n"
        )

        return root_coding_node, list(all_article_annotated_dict.values())


    def generate_coding_nodes(annotations_xlsx_file_path):

        xl = pd.ExcelFile(annotations_xlsx_file_path)

        root_coding_node = None
        df_coding = xl.parse("Liste der Codes")
        num_cols = df_coding.shape[1]
        unused_cols_len = None
        for col_i, col_name in enumerate(df_coding.columns[-1::-1]):
            if "Unnamed" in col_name:
                unused_cols_len = col_i + 1
                break
        parent_of_col_i = {}

        for row in df_coding.iterrows():

            row_data = row[1]
            for col_i in range(num_cols - unused_cols_len + 1):

                col_data = row_data[col_i]

                if type(col_data) == str and col_data != " ":

                    current_parent = parent_of_col_i.get(col_i, None)

                    coding_node = CodingNode(
                        parent=current_parent,
                        coding_value=col_data,
                        anzahl_codings=row_data[-2],
                        anzahl_dokumente=row_data[-1]
                    )
                    parent_of_col_i[col_i + 1] = coding_node
                    if current_parent is None:
                        root_coding_node = coding_node
                    else:
                        current_parent.children.append(coding_node)

                    # SpecialPathCase : BEGIN dirty work-around
                    # for data of Vertiefungsanalyse, where there are duplicate entries
                    # These duplicates were either too complex to filter out automatically
                    # or too time-consuming to do manually. So for that data we assign
                    # the whole category path as value to transform later with transformation rules
                    # If this following code gets commented out, the last column data would be used
                    coding_node.coding_value = coding_node.get_hierarchy_path_as_str()
                    # SpecialPathCase : END

        # SpecialPathCase : BEGIN dirty work-around

        new_str = None
        control_set = set()

        for n in root_coding_node.get_all_subnodes():

            n.coding_path = n.coding_value

            search_str = "Codesystem\Codierung Verwantwortlichkeitsreferenzen \\"

            if n.coding_value.startswith(search_str):

                new_str = n.coding_value.replace(search_str, "")

            else:

                new_str = n.coding_value.split("\\")[-1]

            if not new_str in control_set:

                control_set.add(new_str)

            else:

                raise Exception("Duplicate detected!")

            n.coding_value = new_str

        # SpecialPathCase : END

        return root_coding_node


    def parse_xml_articles(articles_xml_directory, root_coding_node, limit_percent_data):

        def fix_xml_file_content(content_old):

            def main():

                # For now there are a few xml validation errors. Those are fixed on the fly by the following functions:
                # TODO: remove once not needed anymore
                content_new = fix_missing_p_endings(content_old)
                content_new = fix_wrong_file_ending(content_new)
                return content_new

            def fix_missing_p_endings(content_old):

                content_was_changed = False
                content_new = ""
                found_p = False

                for line_old in content_old.splitlines(keepends=True):
                    if line_old.startswith("<p"):
                        found_p = True
                        content_new += line_old
                    elif line_old.startswith("<") and not line_old.startswith("</p>") and found_p:
                        found_p = False
                        content_new += "</p>" + line_old
                        content_was_changed = True
                    else:
                        content_new += line_old

                if content_was_changed:
                    if content_new == content_old:
                        raise Exception(
                            "error in fix_missing_p_endings, content was supposedly fixed, but is still the same.")
                else:
                    if content_new != content_old:
                        raise Exception(
                            "error in fix_missing_p_endings, content was supposedly not fixed, but was changed nevertheless.")

                return content_new


            def fix_wrong_file_ending(content_old):

                content_was_changed = False
                content_new = ""

                for line_old in content_old.splitlines(keepends=True):
                    if line_old.endswith("</file>"):
                        content_new += line_old.replace("</file>", "")
                        content_was_changed = True
                    else:
                        content_new += line_old

                if content_was_changed:
                    if content_new == content_old:
                        raise Exception(
                            "error in fix_wrong_file_ending, content was supposedly fixed, but is still the same.")
                else:
                    if content_new != content_old:
                        raise Exception(
                            "error in fix_wrong_file_ending, content was supposedly not fixed, but was changed nevertheless.")

                return content_new

            return main()


        def get_text_of_all_child_nodes(node):

            all_texts = ""
            for child_node in node:
                all_texts += get_text_of_all_child_nodes(child_node)
            all_texts += node.text

            return all_texts


        all_article_annotated_dict = {}
        removed_xml_brackets = set()
        count_successful = 0
        count_not_successful = 0

        all_article_file_name_list = os.listdir(articles_xml_directory)
        limit = round(len(all_article_file_name_list) / 100 * limit_percent_data)

        for article_file_name in all_article_file_name_list[:limit]:

            if (
                article_file_name.endswith(".3_swp")
                or article_file_name.endswith(".swo")
                or article_file_name.endswith(".swp")
            ):
                continue

            full_article_path = articles_xml_directory + "/" + article_file_name

            with open(full_article_path, "r") as f:

                xml_file_content = f.read()

                aa = ArticleAnnotated(
                    article_file_name=article_file_name,
                    id=xml_file_content.split('<doc id="')[1].split('"')[0],
                    article_file_content=xml_file_content,
                    article_file_content_cleaned=re.sub("<.*?>", "", xml_file_content),
                    root_coding_node=root_coding_node
                )

                for find in re.findall("<.*?>", xml_file_content):

                    # To just give an overview of what elements were removed,
                    # take the first few charcters of it nad print them later
                    removed_xml_brackets.add(find[0:7])

                if aa.article_id in all_article_annotated_dict:
                    raise Exception("Already processed this file!")
                all_article_annotated_dict[aa.article_id] = aa

                # Try to parse it as xml
                try:

                    fixed_xml_file_content = fix_xml_file_content(xml_file_content)
                    if fixed_xml_file_content != xml_file_content:
                        log_manager.info_global(f"Fixed file: {article_file_name}")

                    xml_root_node = ET.fromstring(fixed_xml_file_content)
                    article_content_dict = xml_root_node.attrib.copy()
                    aa.__dict__.update(article_content_dict)

                    stichwort_list = []

                    for child_node in xml_root_node:

                        attrib = child_node.attrib

                        if len(attrib) >= 1:

                            if attrib["name"] == "titel":
                                aa.field_titel =child_node.text

                                if len(child_node) > 1:
                                    raise Exception("This indicates several titles.")

                            elif attrib["name"] == "inhalt":

                                if child_node.getchildren() == []:
                                    aa.field_inhalt =child_node.text

                                else:
                                    log_manager.info_global(
                                        "Inhalts node has children, could not parse file unambiguously. "
                                        "This ArticleAnnotated instance will have no 'field_inhalt'"
                                    )
                                    # raise Exception("Inhalts node has children, could not parse file unambiguously.")

                            elif "dupl" in attrib and attrib["dupl"] == "ftitle":
                                aa.dupl_ftitle =child_node.text

                            elif "name" in attrib and attrib["name"] == "stichwort":
                                stichwort_list.append(child_node.text)

                            else:
                                raise Exception()

                            aa.field_stichwort =stichwort_list

                        else:
                            raise Exception()

                    with open(full_article_path, "r") as f:
                        aa.article_file_content =f.read()

                    count_successful += 1

                except Exception as ex:

                    log_manager.info_global(f"{ex.__class__.__name__}: when parsing file: {article_file_name}: {ex}")
                    count_not_successful += 1

        log_manager.info_global("First few chracters of all xml tags (supposedly) that were removed from content strings:")
        for r in removed_xml_brackets:
            log_manager.info_global(r)

        return all_article_annotated_dict, count_successful, count_not_successful


    def connect_codings_with_articles(annotations_xlsx_file_path, article_annotated_dict, root_coding_node):

        xl = pd.ExcelFile(annotations_xlsx_file_path)
        df_codings_on_articles = xl.parse("Codings")

        count_sucessful = 0
        count_not_sucessful = 0

        for row in df_codings_on_articles.iterrows():

            row_data = row[1]

            try:

                article_annotated = article_annotated_dict[row_data.Dokumentname]

                try:
                    corrected_anfang, corrected_ende = article_annotated.correct_anfang_ende(
                        anfang=row_data.Anfang,
                        ende=row_data.Ende,
                        segment_for_check=row_data.Segment
                    )
                except:
                    corrected_anfang = -1
                    corrected_ende = -1

                article_annotated.add_coding(
                    coding_anfang=corrected_anfang,
                    coding_ende=corrected_ende,
                    coding_tag=row_data.Code,
                    coding_segment=row_data.Segment
                )

                count_sucessful += 1

            except Exception as ex:

                log_manager.info_global(f"{ex.__class__.__name__}: when integrating codings into article: {row_data.Dokumentname}: {ex}")
                count_not_sucessful += 1

        return count_sucessful, count_not_sucessful

    return main()


def create_cats_overview(
    gold_data_container: GoldDataContainer,
    root_coding_node: CodingNode,
    article_annotated_list: List[ArticleAnnotated]
) -> GoldDataContainer:

    # TODO : remove this once sure it's not needed anymore
    def save_cats_hierarchy_into_dict(current_coding_node: CodingNode):

        cats_dict = {}

        for c in current_coding_node.children:
            cats_dict.update(save_cats_hierarchy_into_dict(c))

        return {current_coding_node.coding_value: cats_dict}


    # TODO : remove this once sure it's not needed anymore
    def save_cats_dict_into_list(cat_dict):

        current_leafs_list = []

        for k, v in cat_dict.items():

            if v != {}:

                current_leafs_list.extend(save_cats_dict_into_list(v))

            else:

                current_leafs_list.append(k)

        return current_leafs_list


    def filter_out_unused_cats(
            root_coding_node: CodingNode,
            article_annotated_list: List[ArticleAnnotated],
    ) -> List[str]:

        len_all_aa_list = len(article_annotated_list)
        all_cats_used_list = []

        for cn in root_coding_node.get_all_subnodes():

            len_aa_set = len(cn.article_annotated_set)

            if len_aa_set != 0 and len_aa_set != len_all_aa_list:

                if cn.coding_value in all_cats_used_list:

                    raise Exception(
                        "Category was already added to this list. Such redundancies could interfer later with training "
                        "where categories are used as keys for dictionaries."
                    )

                all_cats_used_list.append(cn.coding_value)

        return all_cats_used_list


    gold_data_container.cats_list = filter_out_unused_cats(root_coding_node, article_annotated_list)

    return gold_data_container

def transform_to_gold_data_articles(
    root_coding_node: CodingNode,
    article_annotated_list: List[ArticleAnnotated],
) -> GoldDataContainer:

    gold_data_container = GoldDataContainer()

    gold_data_container = create_cats_overview(gold_data_container, root_coding_node, article_annotated_list)

    def save_gold_data_into_container(
        gold_data_container: GoldDataContainer,
        article_annotated_list: List[ArticleAnnotated],
    ) -> GoldDataContainer:

        gold_data_container.gold_data_item_list = []

        def get_cats_assigned(article_annotated, cats_list):

            article_cats_dict = {}

            assigned_cats = set(
                coding_dict["coding_node"].coding_value
                for coding_dict in article_annotated.coding_list
            )

            for cat in cats_list:

                if cat in assigned_cats:

                    article_cats_dict[cat] = 1

                else:

                    article_cats_dict[cat] = 0

            return article_cats_dict


        for article_annotated in article_annotated_list:

            gold_data_container.gold_data_item_list.append(
                GoldDataItem(
                    article_id=article_annotated.article_id,
                    text=article_annotated.article_file_content_cleaned,
                    cats=get_cats_assigned(article_annotated, gold_data_container.cats_list)
                )
            )

        return gold_data_container

    gold_data_container = save_gold_data_into_container(
        gold_data_container=gold_data_container,
        article_annotated_list=article_annotated_list,
    )

    return gold_data_container


def transform_to_gold_data_sentences(
    spacy_base_model: str,
    root_coding_node: CodingNode,
    article_annotated_list: List[ArticleAnnotated],
    sentence_split_func,
):

    gold_data_container = GoldDataContainer()

    gold_data_container = create_cats_overview(gold_data_container, root_coding_node, article_annotated_list)

    def save_gold_data_into_container(
        gold_data_container: GoldDataContainer,
        article_annotated_list: List[ArticleAnnotated],
    ):

        cats_list = gold_data_container.cats_list
        gold_data_container.gold_data_item_list = []

        log_manager.info_global(
            "Starting to transform articles with annotations to sentences with annotations.\n"
            "This will take a while."
        )

        len_article_annotated_list = len(article_annotated_list)
        for i, article_annotated in enumerate(article_annotated_list, start=1):
            if i % 100 == 0 or i % len_article_annotated_list == 0:
                log_manager.info_global(f"at article number: {i}, out of {len_article_annotated_list}")

            sentence_cats_dict = OrderedDict()
            sentence_article_list = sentence_split_func(article_annotated.article_file_content_cleaned)

            for sentence in sentence_article_list:

                sentence_cats_dict[str(sentence)] = {cat: 0 for cat in cats_list}

            for coding in article_annotated.coding_list:

                segment = coding["Segment"]
                segment = re.sub("<.*?>", "", segment)
                sentence_segment_list = sentence_split_func(segment)

                for sentence_segment in sentence_segment_list:

                    for sentence_article in sentence_cats_dict.keys():

                        if str(sentence_segment) in sentence_article:

                            cat = coding["coding_node"].coding_value
                            cat_used_dict = sentence_cats_dict[sentence_article]
                            if cat in cat_used_dict:
                                cat_used_dict[cat] = 1

                            break

            for sentence, cats in sentence_cats_dict.items():

                gold_data_container.gold_data_item_list.append(
                    GoldDataItem(
                        article_id=article_annotated.article_id,
                        text=sentence,
                        cats=cats
                    )
                )

        log_manager.info_global(
            f"Transformed {len(article_annotated_list)} articles into {len(gold_data_container.gold_data_item_list)} sentences."
        )

        return gold_data_container


    gold_data_container = save_gold_data_into_container(
        gold_data_container=gold_data_container,
        article_annotated_list=article_annotated_list,
    )

    return gold_data_container
