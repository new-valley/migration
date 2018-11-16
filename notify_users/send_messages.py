#!/usr/bin/env python3


import json
import argparse
import os
import user as u


_FILE_DIR = os.path.abspath(os.path.dirname(__file__))
DEF_WEBDRIVER_PATH = os.path.abspath(
    os.path.join(_FILE_DIR, '..', 'data', 'chromedriver'))
MAX_N_RETRIES = 2
DEF_DST_PATH = './send-messages-status.json'


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    return data


@u.retry(MAX_N_RETRIES)
def send_message(user, recipient, subject, message):
    user.send_message(recipient, subject, message)


def _send_messages(user, messages):
    infos = []
    for i, msg in enumerate(messages):
        info = {
            'message': msg,
            'status': 'success',
        }
        print('in message {}/{}'.format(i+1, len(messages)))
        print('\tto: {} | subject: {}'.format(
            msg['recipient'], msg['subject']))
        send_message(user, msg['recipient'], msg['subject'], msg['message'])
        if not user.success_sending_message():
            print('\tERROR sending message')
            info['status'] = 'fail'
        infos.append(info)
    return infos


def send_messages(email, password, src_path, dst_path, webdriver_path,
        del_messages=False):
    #assumes message is a JSON file in format of a list of dicts in format
    # recipient: "username",
    # subject: "subject",
    # message: "body of message",
    messages = load_json(src_path)

    user = u.User(email=email, password=password, driver_or_path=webdriver_path)
    user.login()
    if not user.is_logged_in():
        print('ERROR: could not log in!')
        return

    used, limit = user.get_messages_numbers()
    n_messages_left = limit - used
    print('{} messages to send, {} left in in user space'.format(
        len(messages), n_messages_left))
    if len(messages) > n_messages_left:
        if not del_messages:
            print('ERROR: it would be necessary to delete messages'
                'but del_messages param is set to False')
        else:
            print('WARNING: it will be necessary to delete some messages')

    infos = _send_messages(user, messages)
    save_json(dst_path, infos)
    print('saved infos to "{}"'.format(dst_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--email',
        required=True,
        help='user email',
    )
    parser.add_argument(
        '--password',
        required=True,
        help='user password',
    )
    parser.add_argument(
        '--src_path',
        required=True,
        help='path to JSON file with messages',
    )
    parser.add_argument(
        '--dst_path',
        nargs='?',
        help='path to save status .json file ({})'.format(DEF_DST_PATH),
        default=DEF_DST_PATH,
    )
    parser.add_argument(
        '--webdriver_path',
        help='path to chrome webdriver ({})'.format(DEF_WEBDRIVER_PATH),
        default=DEF_WEBDRIVER_PATH,
    )
    parser.add_argument(
        '--del_messages_if_needed',
        help='delete messages if needed',
        default=False,
        nargs='?',
        const=True,
    )
    args = parser.parse_args()

    send_messages(
        email=args.email,
        password=args.password,
        src_path=args.src_path,
        dst_path=args.dst_path,
        webdriver_path=args.webdriver_path,
        del_messages=args.del_messages_if_needed,
    )


if __name__ == '__main__':
    main()
