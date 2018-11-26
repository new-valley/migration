#!/usr/bin/env python3

import random
import datetime as dt
import uuid
import json
import os
import argparse


DEF_SRC_PATH = os.path.join('.', 'profiles.json')
DEF_DST_PATH = os.path.join('.', 'fake-data.json')
DEF_CREATION_DATE = dt.datetime(1982, 11, 30, tzinfo=dt.timezone.utc)


def get_rand_str():
    return str(uuid.uuid4()).split('-')[-1]


def get_rand_email():
    tail = random.randint(3, 10)
    email = '{}@{}.com'.format(get_rand_str(), get_rand_str()[:tail])
    return email


def get_rand_id():
    return random.randint(0, 10**18)


#DEFAULT_SUBFORUM = {
#    'subforum_id': get_rand_id(),
#    'title': 'limbo',
#    'description': 'rip',
#    'position': 666666,
#    'created_at': DEF_CREATION_DATE.isoformat(),
#}


def get_avatar_category(url):
    return url.split('/')[-2].split('%')[0].lower()


def get_avatar(uri):
    return {
        'avatar_id': get_rand_id(),
        'uri': uri,
        'category': get_avatar_category(uri),
        'created_at': DEF_CREATION_DATE.isoformat(),
    }


def get_datetime_from_date_str(date_str):
    year, month, day = date_str.split('-')
    return dt.datetime(int(year), int(month), int(day), tzinfo=dt.timezone.utc)


def get_user(username, registration_date, avatar_id, n_topics, n_posts):
    return {
        'user_id': get_rand_id(),
        'avatar_id': avatar_id,
        'username': username,
        'password': get_rand_str(),
        'email': get_rand_email(),
        'created_at': get_datetime_from_date_str(registration_date).isoformat(),
        'roles': 'user',
        'status': 'active',
        'n_topics': n_topics,
        'n_posts': n_posts,
        'signature': 'usuário migrado, abraços',
    }


def get_data(profiles):
    avatars = {}
    users = []
    subforums = []
    topics = []
    posts = []
    for i, prof in enumerate(profiles):
        print('in profile #{}/{}...'.format(i+1, len(profiles)), flush=True,
            end='   \r')
        #creating avatar if needed
        if not prof['avatar_url'] in avatars:
            avatars[prof['avatar_url']] = get_avatar(uri=prof['avatar_url'])
        #creating user
        user = get_user(
            username=prof['username'],
            registration_date=prof['registration_date'],
            avatar_id=avatars[prof['avatar_url']]['avatar_id'],
            n_topics=prof['n_topics'],
            n_posts=prof['n_posts'],
        )
        users.append(user)
    print()
    avatars = list(avatars.values())
    return {
        'subforums': subforums,
        'avatars': avatars,
        'users': users,
        'topics': topics,
        'posts': posts,
    }


def gen_data_for_db_from_profiles(src_path, dst_path, pretty=False):
    #assumes profiles is either output of extract_profiles.py script
    #or just a list of profiles dicts (without the wrapping meta info)
    with open(src_path) as f:
        profiles = json.load(f)
    #direct output of extract_profiles.py
    if profiles and 'status' in profiles[0]:
        profiles = [p['profile'] for p in profiles if p['status'] == 'success']

    print('generating...', flush=True)
    data = get_data(profiles)

    print('saving...', flush=True)
    with open(dst_path, 'w', encoding='utf-8') as f:
        if pretty:
            json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)
        else:
            json.dump(data, f, ensure_ascii=False)
    print('saved generated data to "{}"'.format(dst_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src_path',
        nargs='?',
        help='path to profiles JSON source file (default={})'.format(
            DEF_SRC_PATH),
        default=DEF_SRC_PATH,
    )
    parser.add_argument(
        '--dst_path',
        nargs='?',
        help='path to save resulting JSON file ({})'.format(DEF_DST_PATH),
        default=DEF_DST_PATH,
    )
    parser.add_argument(
        '--pretty',
        nargs='?',
        help='user pretty formatting in output file (uses more space) (False)',
        const=True,
        default=False,
    )
    args = parser.parse_args()

    gen_data_for_db_from_profiles(
        src_path=args.src_path,
        dst_path=args.dst_path,
        pretty=args.pretty,
    )


if __name__ == '__main__':
    main()
