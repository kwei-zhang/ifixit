#!/usr/bin/env python

from os.path import exists, join, isfile
from os import listdir
import json

from ifixittozim import logger, LANGS
from ifixittozim.utils import get_api_content, get_cache_path

def get_guides(ifixit_api_base_url):

    cache_path = get_cache_path()

    guide_ids = set()

    for lang in LANGS:
        cur_path = join(cache_path, 'categories', lang)
        for category_filename in listdir(cur_path):
            category_path = join(cur_path,category_filename)
            with open(category_path, 'r', encoding='utf-8') as category_file:
                category_content = json.load(category_file)
                if not category_content:
                    continue
                try:
                    for guide in category_content['guides']:
                        guide_ids.add(guide['guideid'])
                    for guide in category_content['featured_guides']:
                        guide_ids.add(guide['guideid'])
                except:
                    logger.warning('\tFailed to process {}'.format(category_path))
    
    logger.info('\t{} guides found'.format(len(guide_ids)))

    guide_num = 1

    for guide_id in guide_ids:
        for lang in LANGS:
            cache_file_path = join(cache_path, 'guides', lang, "guide_{}.json".format(guide_id))
            if exists(cache_file_path):
                continue
            logger.info("\tRetrieving guide '{}' in {} ({}/{})".format(guide_id, lang, guide_num, len(guide_ids)))
            guide_content = get_api_content(ifixit_api_base_url, "/guides/{}?langid={}".format(guide_id, lang))
            with open(cache_file_path, 'w', encoding='utf-8') as cachefile:
                json.dump(guide_content, cachefile, ensure_ascii=False, indent=4)
        guide_num += 1
