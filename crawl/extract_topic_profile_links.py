#!/usr/bin/env python3

import argparse
import os
import common


DEF_WEBDRIVER_PATH = os.path.abspath('chromedriver')
DEF_PAGE_LOAD_TIMEOUT = 3#25
MAX_SUCCESSIVE_FAILS = 10
MAX_N_RETRIES = 3


@common.retry(MAX_N_RETRIES)
def get_profile_links_from_topic_page(driver, url=None, verbose=True):
    common.load_page(driver, url, verbose)
    elems = driver.find_elements_by_class_name('perfil')
    links = []
    for elem in elems:
        links.append(elem.find_element_by_tag_name('a').get_attribute('href'))
    return links


def infinite(start=0, step=1):
    i = start
    while True:
        yield i
        i += step


def get_profile_links_from_topic(
        driver, url, start_page=1, only_pages=None, verbose=True):
    info = print if verbose else silence
    base_url = driver.current_url if url is None else url
    fail_count = 0
    links = []
    pages = infinite(start_page) if only_pages is None else only_pages
    for page in pages:
        url = '{}?page={}'.format(base_url, page)
        try:
            links_ = get_profile_links_from_topic_page(driver, url, verbose)
            if not links_:
                break
            data = {
                'page': page,
                'status': 'success',
                'message': '',
                'links': links_,
            }
            fail_count = 0
        except Exception as e:
            info('ERROR in page {}: "{}"'.format(page, e))
            data = {
                'page': page,
                'status': 'fail',
                'message': '{}'.format(e),
                'links': [],
            }
            fail_count += 1
        if fail_count > MAX_SUCCESSIVE_FAILS:
            print('MAX_SUCCESSIVE_FAILS reached')
            break
        links.append(data)
    return links


def extract_topic_profile_links(
        url, start_page, only_pages, dst_path,
        webdriver_path, page_load_timeout
    ):
    driver = common.get_headless_chrome_browser(
        webdriver_path, page_load_timeout)
    links = get_profile_links_from_topic(driver, url, start_page, only_pages)
    common.save_json(dst_path, links)
    print('saved pages to "{}"'.format(dst_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--url',
        required=True,
        help='url of topic'
    )
    parser.add_argument(
        '--dst_path',
        required=True,
        help='path to save links .json file',
    )
    parser.add_argument(
        '--start_page',
        help='page number to start (1-indexed)',
        default=1,
    )
    parser.add_argument(
        '--only_pages',
        help='explore only these pages',
        nargs='*',
        default=None,
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

    extract_topic_profile_links(
        url=args.url,
        dst_path=args.dst_path,
        webdriver_path=args.webdriver_path,
        start_page=args.start_page,
        only_pages=args.only_pages,
        page_load_timeout=args.page_load_timeout,
    )


if __name__ == '__main__':
    main()
