import random
import requests
import re
import urllib.parse
from loggers import log_manager

session = None

def create_session(ske_config):

    global session

    if not session:
        log_manager.debug_global("Creating HTTP session ...")
        session = requests.Session()
        session.auth = (ske_config['ske_user'], ske_config['ske_password'])


def close_session():

    global session 

    if session:
        log_manager.debug_global("Closing HTTP session ...")
        session.close()
        session = None


def clean_text(text):

    text = text.\
        replace('<i class="strc">&lt;s&gt;&lt;/doc&gt;</i>', "").\
        replace('<i class="strc">&lt;/doc&gt;</i>', "").\
        replace('<i class="strc">&lt;doc&gt;</i>', "").\
        replace('<i class="strc">&lt;s&gt;</i>', "").\
        replace("<i class='strc'>&lt;p&gt;</i>", "").\
        replace('<i class="coll">&gt;</i>', "").\
        replace('<i class="strc"></i>\n', "").\
        replace('<br/>\n', "").\
        replace('<i class="coll">', "").\
        replace('</i>\n', "").\
        replace('&gt;', "")

    # Models were traind on texts with plenty of "\n", so better not remove them (for now)
    # text = re.sub("(\\n|  +)+", "", text)

    return text


def get_corpus_info(ske_config):

    create_session(ske_config)

    response = session.request(
        method="GET",
        url=ske_config["ske_rest_url"] + "/first",
        params={
            "corpname": ske_config["ske_corpus_id"],
            "queryselector": "cqlrow",
            "cql": "<doc> []",
            "format": "json",
        }
    )

    return response.json()


def get_last_pos(ske_config):

    ci = get_corpus_info(ske_config)
    np = ci["numofpages"]
    pi = get_page_info(ske_config, np)

    return pi["Lines"][-1]["toknum"]


def get_page_info(ske_config, page_index):

    create_session(ske_config)

    response = session.request(
        method="GET",
        url=ske_config["ske_rest_url"] + "/first",
        params={
            "corpname": ske_config["ske_corpus_id"],
            "queryselector": "cqlrow",
            "cql": "<doc> []",
            "format": "json",
            "fromp": page_index
        }
    )

    return response.json()


def iterate_over_pos_of_corpus(ske_config):

    log_manager.info_global(f"Fetching all pos from corpus {ske_config['ske_corpus_id']}")
    corpus_info = get_corpus_info(ske_config)
    numofpages = corpus_info["numofpages"]
    log_manager.info_global(f"Iterating over {numofpages} pages")

    for page in range(1, numofpages + 1):
        page_info = get_page_info(ske_config, page)
        for p in page_info["Lines"]:
            yield p["toknum"]


def get_doc_from_pos(ske_config, pos):

    create_session(ske_config)

    response = session.request(
        method="GET",
        url=ske_config["ske_rest_url"] + "/structctx",
        params={
            "corpname": ske_config["ske_corpus_id"],
            "pos": pos
        }
    )

    text_cleaned = clean_text(response.text)
    url = response.url

    return {
        "text": text_cleaned,
        "url": url
    }


def get_pos_from_docid(ske_config, docid):

    create_session(ske_config)

    response = session.request(
        method="GET",
        url=ske_config["ske_rest_url"] + "/first",
        params={
            "corpname": ske_config["ske_corpus_id"],
            "queryselector": "cqlrow",
            "cql": f'<doc id="{docid}"> []',
            "format": "json"
        }
    )

    pos = response.json()['Lines'][0]['toknum']

    return pos


def get_pos_from_url(url):

    parseresult = urllib.parse.urlparse(url)
    querystring = parseresult.query
    params = urllib.parse.parse_qs(querystring)
    pos = params['pos']
    assert len(pos) == 1
    return pos[0]


def get_docid_from_pos(ske_config, pos):

    create_session(ske_config)

    response = session.request(
        method="GET",
        url=ske_config["ske_rest_url"] + "/fullref",
        params={
            "corpname": ske_config["ske_corpus_id"],
            "pos": pos,
            "format": "json"
        }
    )

    docid = response.json()['doc_id']

    return docid


def get_url_from_pos(ske_config, pos):

    clean_rest_url = ske_config['ske_rest_url']
    if clean_rest_url[-1] == '/':
        clean_rest_url = clean_rest_url[:-1]

    return f"{clean_rest_url}/structctx?corpname={ske_config['ske_corpus_id']}&pos={pos}"


def get_doc_from_docid(ske_config, docid):

    pos = get_pos_from_docid(ske_config, docid)

    return get_doc_from_pos(ske_config, pos)


def get_doc_from_url(ske_config, url):

    create_session(ske_config)

    response = session.request(
        method="GET",
        url=url,
    )

    text_cleaned = clean_text(response.text)
    url = response.url

    return {
        "text": text_cleaned,
        "url": url
    }


def get_random_doc(ske_config):

    corpus_info = get_corpus_info(ske_config)
    numofpages = corpus_info["numofpages"]

    random_page_index = random.randint(1, numofpages)
    page_info = get_page_info(ske_config, random_page_index)
    random_item = random.choice(page_info["Lines"])

    random_toknum = random_item["toknum"]
    return get_doc_from_pos(ske_config, random_toknum)
