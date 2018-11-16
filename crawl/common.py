from selenium import webdriver
import json

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)

def load_json(path):
    with open(path) as f:
        data = json.load(f)
    return data

def get_headless_chrome_browser(webdriver_path, page_load_timeout=None):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(webdriver_path, chrome_options=options)
    if page_load_timeout is not None:
        driver.set_page_load_timeout(page_load_timeout)
    return driver

def load_page(driver, url=None, verbose=True):
    info = print if verbose else silence
    if url is not None:
        info('acessing "{}"...'.format(url), flush=True, end=' ')
        driver.get(url)
        info('done')
    return driver

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
