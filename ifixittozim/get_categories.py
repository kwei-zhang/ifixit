#!/usr/bin/env python

from os.path import exists, join
import json

# from sqlalchemy import create_engine
# from sqlalchemy.sql import text

from ifixittozim import logger, LANGS
from ifixittozim.utils import get_api_content, get_cache_path

def get_categories(ifixit_api_base_url):

    # eng = create_engine("sqlite:///ifixit2zim.db")
    # con = eng.connect()
    cachePath = get_cache_path()

    categories = get_api_content(ifixit_api_base_url, "/categories?includeStubs=true")
    all_categories = []
    root_categories = []
    for category in categories:
        all_categories.append(category)
        root_categories.append(category)
        process_sub_categories(all_categories, categories[category])
    
    logger.info("\t{} categories found, including {} root categories".format(len(all_categories),len(root_categories)))

    wiki_num = 1
    for category_name in all_categories:
        for lang in LANGS:
            cacheFilePath = join(cachePath, 'categories', lang, "wiki_{}.json".format(category_name))
            if exists(cacheFilePath):
                continue
            logger.info("\tRetrieving wiki details for category '{}' in {} ({}/{})".format(category_name, lang, wiki_num, len(all_categories)))
            category_wiki_details = get_api_content(ifixit_api_base_url, "/wikis/CATEGORY/{}?langid={}".format(category_name, lang))
            with open(cacheFilePath, 'w', encoding='utf-8') as cachefile:
                json.dump(category_wiki_details, cachefile, ensure_ascii=False, indent=4)
        wiki_num += 1

def process_sub_categories(all_categories, categories):
    for category in categories:
        all_categories.append(category)
        process_sub_categories(all_categories, categories[category])