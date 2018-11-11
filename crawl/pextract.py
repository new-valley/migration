#!/usr/bin/env python3

from selenium import webdriver
import datetime as dt
import sys
import json


def return_none_if_fails(fn):
    def wrapper(driver):
        try:
            ret = fn(driver)
        except Exception as e:
            print('ERROR in {}: "{}"'.format(fn.__name__, e))
            ret = None
        return ret
    return wrapper


@return_none_if_fails
def get_username(driver):
    elem = driver.find_element_by_class_name('userName')
    username = elem.text
    return username


@return_none_if_fails
def get_registration_year(driver):
    elem = driver.find_element_by_class_name('points-year')
    year = int(elem.get_attribute('innerHTML'))
    return year


@return_none_if_fails
def get_registration_day_month(driver):
    elem = driver.find_element_by_class_name('points-day-month')
    day, month = elem.get_attribute('innerHTML').split()
    day, month = int(day.strip()), int(month.strip())
    return day, month


@return_none_if_fails
def get_avatar_url(driver):
    elem = driver.find_element_by_class_name('avatarImg')
    url = elem.get_attribute('src')
    return url


@return_none_if_fails
def get_avg_posts_per_day(driver):
    elem = driver.find_element_by_id('posts-per-day')
    posts_per_day = float(elem.text)
    return posts_per_day


@return_none_if_fails
def get_n_posts(driver):
    elem = driver.find_element_by_id('profile-statistics')
    tokens = elem.text.split('\n')
    n_posts = int(tokens[1].split()[0].strip())
    return n_posts


@return_none_if_fails
def get_n_topics(driver):
    elem = driver.find_element_by_id('profile-statistics')
    tokens = elem.text.split('\n')
    if 'não existem tópicos' in tokens[-1].lower():
        n_topics = 0
    else:
        n_topics = int(tokens[-1].strip())
    return n_topics


@return_none_if_fails
def get_level(driver):
    elem = driver.find_element_by_class_name('condecoration-level')
    level = int(elem.text.split()[-1].strip())
    return level


@return_none_if_fails
def get_registration_date(driver):
    year = get_registration_year(driver)
    day, month = get_registration_day_month(driver)
    date = dt.date(year, month, day)
    date = date.isoformat()
    return date


def get_profile(driver, url=None):
    if url is not None:
        driver.get(url)
    data = {
        'profile_url': driver.current_url,
        'username': get_username(driver),
        'registration_date': get_registration_date(driver),
        'n_posts': get_n_posts(driver),
        'n_topics': get_n_topics(driver),
        'avg_posts_per_day': get_avg_posts_per_day(driver),
        'level': get_level(driver),
        'avatar_url': get_avatar_url(driver),
    }
    return data


def _get_headless_chrome_browser(webdriver_path):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(webdriver_path, chrome_options=options)
    return driver


class ProfileExtractor:
    def __init__(self, driver_or_path, verbose=False):
        self.info = print if verbose else (lambda *a, **ka: None)

        self.driver = driver_or_path
        if isinstance(driver_or_path, str):
            self.info('opening driver...', flush=True, end=' ')
            self.driver = _get_headless_chrome_browser(driver_or_path)
            self.info('done')

    def get_profile(self, url):
        self.info('acessing "{}"...'.format(url), flush=True, end=' ')
        self.driver.get(url)
        self.info('done')
        return get_profile(self.driver)


def main():
    url = 'http://forum.jogos.uol.com.br/umvtetudo_u_1275733662567210576'
    if len(sys.argv) > 1:
        url = sys.argv[1]
    extractor = ProfileExtractor(WEBDRIVER_PATH, verbose=True)
    profile = extractor.get_profile(url)
    print('profile:')
    print(profile)
    with open('profile.json', 'w') as f:
        json.dump(profile, f, indent=4, sort_keys=True)
    print('saved to profile.json')

if __name__ == '__main__':
    main()
