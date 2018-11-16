#!/usr/bin/env python3

from selenium import webdriver
from requests.utils import urlparse
import datetime as dt
import sys
import json
import os

_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
DEF_WEBDRIVER_PATH = os.path.abspath(
    os.path.join(_FILE_DIR, '..', 'data', 'chromedriver'))
DEF_PAGE_LOAD_TIMEOUT = 25
MAX_N_RETRIES = 3
FORUM_HOMEPAGE_URL = 'http://forum.jogos.uol.com.br'


def retry(max_n_times=1, verbose=True):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            for i in range(max_n_times):
                try:
                    ret = fn(*args, **kwargs)
                    return ret
                except Exception as e:
                    if verbose:
                        print('FAIL #{} @{}: "{}" - trying again'.format(
                            i+1, fn.__name__, e))
                    exc = e
            else:
                raise exc
        return wrapper
    return decorator


def get_headless_chrome_browser(
        webdriver_path, page_load_timeout=DEF_PAGE_LOAD_TIMEOUT):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(webdriver_path, chrome_options=options)
    if page_load_timeout is not None:
        driver.set_page_load_timeout(page_load_timeout)
    return driver


def is_in_domain(driver, netloc):
    driver_meta = urlparse(driver.current_url)
    return driver_meta.netloc == netloc


def is_in_page(driver, url):
    meta_a = urlparse(url)
    meta_b = urlparse(driver.current_url)
    return all([
        #meta_a.scheme == meta_b.scheme,
        meta_a.netloc == meta_b.netloc,
        #meta_a.path == meta_b.path,
        meta_a.path.rstrip('/') == meta_b.path.rstrip('/'),
    ])


@retry(MAX_N_RETRIES)
def access(driver, url, refresh=False):
    if refresh or not is_in_page(driver, url):
        driver.get(url)


def get_login_url(forum_homepage_url):
    return '{}'.format(forum_homepage_url)


def get_messages_main_url(forum_homepage_url):
    return '{}/inbox.jbb'.format(forum_homepage_url)


def get_messages_inbox_url(forum_homepage_url):
    return '{}/inbox.jbb'.format(forum_homepage_url)


def get_messages_outbox_url(forum_homepage_url):
    return '{}/outbox.jbb'.format(forum_homepage_url)


def get_new_message_url(forum_homepage_url):
    return '{}/new.jbb'.format(forum_homepage_url)


def is_in_forum(driver, forum_homepage_url):
    netloc = urlparse(forum_homepage_url).netloc
    return is_in_domain(driver, netloc)


def get_actions_header_elem(driver_at_login_page):
    elem = driver_at_login_page.find_element_by_id('header-actions')
    return elem


def get_email_field_elem(actions_header_elem):
    elem = actions_header_elem.find_element_by_id('user')
    return elem


def get_password_field_elem(actions_header_elem):
    elem = actions_header_elem.find_element_by_id('pass')
    return elem


def get_login_button_elem(actions_header_elem):
    elem = actions_header_elem.find_element_by_name('submit')
    return elem


def get_logout_button_elem(actions_header_elem):
    elem = actions_header_elem.find_element_by_class_name('logout')
    return elem


def get_messages_header_elem(driver_at_messages_main_page):
    elem = driver_at_messages_main_page.find_element_by_id('mps-main')
    return elem


def get_messages_numbers_elem(messages_header_elem):
    elem = messages_header_elem.find_element_by_id('mps-options')
    return elem


def get_element_by_class_name_and_attribute(driver, class_name, attr, attr_val):
    elems = driver.find_elements_by_class_name(class_name)
    for elem in elems:
        if elem.get_attribute(attr) == attr_val:
            return elem
    else:
        raise ValueError('elem not found')


def get_message_recipient_field_elem(driver_at_new_message_page):
    return get_element_by_class_name_and_attribute(
        driver_at_new_message_page, 'formSend-input', 'name', 'username')


def get_message_subject_field_elem(driver_at_new_message_page):
    return get_element_by_class_name_and_attribute(
        driver_at_new_message_page, 'formSend-input', 'name', 'pm.topic')


def get_message_body_field_elem(driver_at_new_message_page):
    elem = driver_at_new_message_page.find_element_by_id('messageContent')
    return elem


def get_send_message_button_elem(driver_at_new_message_page):
    elem = driver_at_new_message_page.find_element_by_class_name('submit')
    return elem


def get_message_error_elements(driver_after_sending_message):
    return driver_after_sending_message.find_elements_by_class_name(
        'error-msg')


def get_toggle_all_messages_checked_elem(driver_at_inbox_or_outbox):
    elem = driver_at_inbox_or_outbox.find_element_by_class_name(
        'check-uncheck-all')
    return elem


def get_message_checkbox_elems(driver_at_inbox_or_outbox):
    elems = driver_at_inbox_or_outbox.find_elements_by_class_name('select')
    return elems


def get_delete_checked_messages_elem(driver_at_inbox_or_outbox):
    try:
        elem = driver_at_inbox_or_outbox.find_element_by_class_name('red-erase')
    except:
        return None
    return elem


def get_confirm_deletion_checked_outbox_messages_elem(
        driver_at_confirmation_screen):
    elem = driver_at_confirmation_screen.find_element_by_class_name(
        'submitDeleteOutbox')
    elem = elem.find_element_by_class_name('blue-button')
    return elem


def get_confirm_deletion_checked_inbox_messages_elem(
        driver_at_confirmation_screen):
    elem = driver_at_confirmation_screen.find_element_by_class_name(
        'submitDeleteInbox')
    elem = elem.find_element_by_class_name('blue-button')
    return elem


def delete_all_outbox_checked_messages(driver_at_outbox):
    if not any_messages_checked(get_message_checkbox_elems(driver_at_outbox)):
        return
    elem = get_delete_checked_messages_elem(driver_at_outbox)
    click(elem)
    elem = get_confirm_deletion_outbox_messages_elem(driver_at_outbox)
    click(elem)


def delete_all_outbox_messages(driver_at_outbox):
    check_all_messages(driver_at_outbox)
    delete_all_outbox_checked_messages(driver_at_outbox)


def delete_all_inbox_checked_messages(driver_at_inbox):
    if not any_messages_checked(get_message_checkbox_elems(driver_at_inbox)):
        return
    elem = get_delete_checked_messages_elem(driver_at_inbox)
    click(elem)
    elem = get_confirm_deletion_inbox_messages_elem(driver_at_inbox)
    click(elem)


def delete_all_inbox_messages(driver_at_inbox):
    check_all_messages(driver_at_inbox)
    delete_all_inbox_checked_messages(driver_at_inbox)


def toggle_all_messages_checked(driver_at_inbox_or_outbox):
    elem = get_toggle_all_messages_checked_elem(driver_at_inbox_or_outbox)
    click(elem)


def all_messages_checked(elems):
    return all(e.get_property('checked') for e in elems)


def any_messages_checked(elems):
    return any(e.get_property('checked') for e in elems)


def check_all_messages(driver_at_inbox_or_outbox):
    elems = get_message_checkbox_elems(driver_at_inbox_or_outbox)
    for __ in range(2):
        toggle_all_messages_checked(driver_at_inbox_or_outbox)
        if all_messages_checked(elems):
            break
    else:
        raise Exception('should have been able to check everything')


def uncheck_all_messages(driver_at_inbox_or_outbox):
    elems = get_message_checkbox_elems(driver_at_inbox_or_outbox)
    for __ in range(2):
        toggle_all_messages_checked(driver_at_inbox_or_outbox)
        if not any_messages_checked(elems):
            break
    else:
        raise Exception('should have been able to check everything')


def send_message(driver_at_new_message_page, recipient, subject, message):
    if not (recipient and subject and message):
        raise ValueError('fields cannot be empty')
    #filling destiny username
    elem = get_message_recipient_field_elem(driver_at_new_message_page)
    put_text(elem, recipient)
    #filling subject
    elem = get_message_subject_field_elem(driver_at_new_message_page)
    put_text(elem, subject)
    #filling body
    elem = get_message_body_field_elem(driver_at_new_message_page)
    put_text(elem, message)
    #clicking send
    elem = get_send_message_button_elem(driver_at_new_message_page)
    click(elem)


def success_sending_message(driver_after_sending_message):
    elems = get_message_error_elements(driver_after_sending_message)
    return len(elems) == 0


def get_messages_numbers(driver_at_messages_main_page):
    header_elem = get_messages_header_elem(driver_at_messages_main_page)
    elem = get_messages_numbers_elem(header_elem)
    text = elem.text
    assert text.lower().startswith('total:')
    tokens = text.lower().split()
    assert len(tokens) > 1
    assert '/' in tokens[1]
    used, limit = map(int, tokens[1].split('/'))
    return used, limit


def put_text(elem, text, clear=True):
    if clear:
        elem.clear()
    elem.send_keys(text)


def click(elem):
    elem.click()


def login(driver_at_login_page, email, password):
    actions_elem = get_actions_header_elem(driver_at_login_page)
    #putting email
    elem = get_email_field_elem(actions_elem)
    put_text(elem, email)
    #putting password
    elem = get_password_field_elem(actions_elem)
    put_text(elem, password)
    #clicking to login
    elem = get_login_button_elem(actions_elem)
    click(elem)


def is_logged_in(driver_at_forum_page):
    elem = get_actions_header_elem(driver_at_forum_page)
    elems = elem.find_elements_by_class_name('top-user')
    return len(elems) > 0


def logout(driver_logged_in_at_forum_page):
    actions_elem = get_actions_header_elem(driver_logged_in_at_forum_page)
    #logout button
    elem = get_logout_button_elem(actions_elem)
    elem.click()


class User:
    def __init__(self, email, password,
            driver_or_path, forum_homepage_url=FORUM_HOMEPAGE_URL,
            verbose=True):
        self.info = print if verbose else (lambda *a, **ka: None)

        self.email = email
        self.password = password

        self.driver = driver_or_path
        if isinstance(driver_or_path, str):
            self.info('opening driver...', flush=True, end=' ')
            self.driver = get_headless_chrome_browser(driver_or_path)
            self.info('done')

        self.forum_homepage_url = forum_homepage_url.rstrip('/')

    def get_login_url(self):
        return get_login_url(self.forum_homepage_url)

    def get_messages_main_url(self):
        return get_messages_main_url(self.forum_homepage_url)

    def get_messages_inbox_url(self):
        return get_messages_inbox_url(self.forum_homepage_url)

    def get_messages_outbox_url(self):
        return get_messages_outbox_url(self.forum_homepage_url)

    def get_new_message_url(self):
        return get_new_message_url(self.forum_homepage_url)

    def is_in_forum(self):
        return is_in_forum(self.driver, self.forum_homepage_url)

    def access(self, url, refresh=False):
        self.info('acessing "{}"...'.format(url), flush=True, end=' ')
        access(self.driver, url, refresh=refresh)
        self.info('done.')

    def access_forum_homepage_if_not_in_forum(self):
        if not self.is_in_forum():
            self.access(self.forum_homepage_url)

    def login(self):
        self.access(self.get_login_url())
        login(self.driver, self.email, self.password)

    def is_logged_in(self):
        self.access_forum_homepage_if_not_in_forum()
        return is_logged_in(self.driver)

    def logout(self):
        self.access_forum_homepage_if_not_in_forum()
        logout(self.driver)

    def access_messages_main_page(self):
        self.access(self.get_messages_main_url())

    def access_messages_inbox(self):
        self.access(self.get_messages_inbox_url())

    def access_messages_outbox(self):
        self.access(self.get_messages_outbox_url())

    def access_new_message_page(self):
        self.access(self.get_new_message_url())

    def get_messages_numbers(self):
        self.access_messages_main_page()
        used, limit = get_messages_numbers(self.driver)
        return used, limit

    def get_n_used_messages(self):
        return self.get_messages_numbers()[0]

    def get_n_limit_messages(self):
        return self.get_messages_numbers()[1]

    def send_message(self, recipient, subject, message):
        self.access_new_message_page()
        send_message(self.driver, recipient, subject, message)

    def success_sending_message(self):
        return success_sending_message(self.driver)

    def delete_all_outbox_checked_messages(self):
        self.access_messages_outbox()
        delete_all_outbox_checked_messages(self.driver)

    def delete_all_inbox_checked_messages(self):
        self.access_messages_inbox()
        delete_all_inbox_checked_messages(self.driver)

    def delete_all_outbox_messages(self):
        self.access_messages_outbox()
        delete_all_outbox_messages(self.driver)

    def delete_all_inbox_messages(self):
        self.access_messages_inbox()
        delete_all_inbox_messages(self.driver)

    def delete_all_messages(self):
        self.delete_all_outbox_messages()
        self.delete_all_inbox_messages()
