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


class NoMessageSpaceLeft(Exception):
    pass


def check_messages_numbers_and_delete_if_needed(
        user, min_space=1, try_inbox=False):
    n_msgs_used, n_msgs_limit = user.get_messages_numbers()
    if n_msgs_limit - n_msgs_used < min_space:
        #trying to free up space first in outbox
        print('\tlimit messages reached, deleting outbox messages')
        user.delete_all_outbox_messages()
        n_msgs_used, n_msgs_limit = user.get_messages_numbers()
        if n_msgs_limit - n_msgs_used < min_space:
            if try_inbox:
                print('\tlimit messages reached, deleting inbox messages')
                user.delete_all_inbox_messages()
            else:
                raise NoMessageSpaceLeft('could not free up messages space')


def _send_messages(user, messages, start=0):
    infos = []
    for i in range(start, len(messages)):
        msg = messages[i]
        print('in message {}/{}'.format(i+1, len(messages)))
        print('\tto: {} | subject: {}'.format(
            msg['recipient'], msg['subject']))
        info = {
            'message': msg,
            'status': 'success',
            'status_message': 'message sent'
        }
        try:
            check_messages_numbers_and_delete_if_needed(user, min_space=3)
            send_message(user, msg['recipient'], msg['subject'], msg['message'])
            if not user.success_sending_message():
                print('\tERROR: no success sending message')
                info['status'] = 'fail'
                info['status_message'] = 'no success sending message'
        except NoMessageSpaceLeft:
            raise
        except Exception as e:
            print('\tERROR: {}'.format(e))
            info['status'] = 'fail'
            info['status_message'] = str(e)
        infos.append(info)
    return infos


def send_messages(email, password, src_path, dst_path, webdriver_path,
        del_messages=False, start_from=1):
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
        len(messages) - start_from, n_messages_left))
    if len(messages) - start_from > n_messages_left:
        if not del_messages:
            print('ERROR: it would be necessary to delete messages'
                'but del_messages param is set to False')
            return
        else:
            print('WARNING: it will be necessary to delete some messages')

    infos = _send_messages(user, messages, start_from-1)
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
    parser.add_argument(
        '--start_from',
        help='start from this message (1-indexed)',
        default=1,
        type=int,
    )
    args = parser.parse_args()

    send_messages(
        email=args.email,
        password=args.password,
        src_path=args.src_path,
        dst_path=args.dst_path,
        webdriver_path=args.webdriver_path,
        del_messages=args.del_messages_if_needed,
        start_from=args.start_from,
    )


if __name__ == '__main__':
    main()
