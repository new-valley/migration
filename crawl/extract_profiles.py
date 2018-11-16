#!/usr/bin/env python3

import argparse
import os
import pextract
import common


DEF_WEBDRIVER_PATH = os.path.abspath('chromedriver')
DEF_PAGE_LOAD_TIMEOUT = 25
MAX_SUCCESSIVE_FAILS = 10
MAX_N_RETRIES = 3


def silence(*args, **kwargs):
    pass


@common.retry(MAX_N_RETRIES)
def get_profile(driver, url):
    return pextract.get_profile(driver, url)


def extract_profiles(driver, links, verbose=True):
    info = print if verbose else silence
    links = set(links)
    fail_count = 0
    extract_profiles = []
    for i, url in enumerate(links):
        info('in url {}/{} "{}"'.format(i+1, len(links), url))
        try:
            profile = get_profile(driver, url)
            data = {
                'url': url,
                'status': 'success',
                'message': '',
                'profile': profile,
            }
            extract_profiles.append(data)
            fail_count = 0
        except Exception as e:
            info('ERROR in url {}: "{}"'.format(url, e))
            data = {
                'url': url,
                'status': 'fail',
                'message': '{}'.format(e),
                'profile': None,
            }
            fail_count += 1
        if fail_count > MAX_SUCCESSIVE_FAILS:
            print('MAX_SUCCESSIVE_FAILS reached')
            break
    return extract_profiles


def flatten(lst):
    return [item for sublst in lst for item in sublst]


def _extract_profiles(src_path, dst_path, webdriver_path, page_load_timeout):
    #if json, assumes its output of extract_topic_profile_links
    if src_path.endswith('.json'):
        links = common.load_json(src_path)
        links = flatten([d['links'] for d in links])
    #else, assumes its a simple links list
    else:
        with open(src_path) as f:
            links = [l.strip() for l in f]
    driver = common.get_headless_chrome_browser(
        webdriver_path, page_load_timeout)
    profiles = extract_profiles(driver, links)
    common.save_json(dst_path, profiles)
    print('saved profiles to "{}"'.format(dst_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src_path',
        required=True,
        help='path to links',
    )
    parser.add_argument(
        '--dst_path',
        required=True,
        help='path to save profiles .json file',
    )
    parser.add_argument(
        '--webdriver_path',
        help='path to chrome webdriver ({})'.format(DEF_WEBDRIVER_PATH),
        default=DEF_WEBDRIVER_PATH,
    )
    parser.add_argument(
        '--page_load_timeout',
        help='page load timeout in seconds ({})'.format(DEF_PAGE_LOAD_TIMEOUT),
        default=DEF_PAGE_LOAD_TIMEOUT,
    )
    args = parser.parse_args()

    _extract_profiles(
        src_path=args.src_path,
        dst_path=args.dst_path,
        webdriver_path=args.webdriver_path,
        page_load_timeout=args.page_load_timeout,
    )


if __name__ == '__main__':
    main()
