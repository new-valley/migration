#!/usr/bin/env python3


import argparse
import requests
import json


API_URL = 'http://ec2-18-231-167-148.sa-east-1.compute.amazonaws.com:7310/api'
DEF_DST_PATH = './filtered-migration-data.json'


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    return data


def get_all_users():
    resp = requests.get('{}/users?max_n_results=999999'.format(API_URL))
    assert resp.status_code == 200
    assert resp.json()['total'] <= 999999
    users = resp.json()['data']
    return users


def get_all_avatars():
    resp = requests.get('{}/avatars?max_n_results=999999'.format(API_URL))
    assert resp.status_code == 200
    assert resp.json()['total'] <= 999999
    avatars = resp.json()['data']
    return avatars


def filter_existing_data(src_path, dst_path):
    migration_data = load_json(src_path)
    #users
    all_users = get_all_users()
    usernames = {u['username'] for u in all_users}
    old_n_users = len(migration_data['users'])
    migration_data['users'] = [\
        u for u in migration_data['users'] if u['username'] not in usernames]
    print('filtered from {} to {} users using {} existing usernames'.format(
        old_n_users, len(migration_data['users']), len(usernames)))
    #avatars
    all_avatars = get_all_avatars()
    avatar_ids = {a['avatar_id'] for a in all_avatars}
    old_n_avatars = len(migration_data['avatars'])
    migration_data['avatars'] = [\
        a for a in migration_data['avatars'] \
            if str(a['avatar_id']) not in avatar_ids]
    print('filtered from {} to {} avatars using {} existing avatar_ids'.format(
        old_n_avatars, len(migration_data['avatars']), len(avatar_ids)))

    save_json(dst_path, migration_data)
    print('saved to', dst_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src_path',
        required=True,
        help='path to JSON migration data',
    )
    parser.add_argument(
        '--dst_path',
        nargs='?',
        help='path to save result file ({})'.format(DEF_DST_PATH),
        default=DEF_DST_PATH,
    )
    args = parser.parse_args()

    filter_existing_data(
        src_path=args.src_path,
        dst_path=args.dst_path
    )


if __name__ == '__main__':
    main()
