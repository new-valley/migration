#!/usr/bin/env python3

import argparse
import os
import common
import requests
import hashlib


DEF_DST_DIR_PATH = os.path.join(os.getcwd(), 'avatars')


def silence(*args, **kwargs):
    pass


def download(url, dst_path):
    resp = requests.get(url)
    with open(dst_path, 'wb') as f:
        f.write(resp.content)
    return dst_path


def get_dst_avatar_path(profile, base_dir):
    url = profile['avatar_url']
    hashed_url = hashlib.sha1(url.encode('utf-8')).hexdigest()
    ext = url.split('.')[-1]
    filename = '{}.{}'.format(hashed_url, ext)
    path = os.path.join(base_dir, filename)
    return path


def download_avatars(src_path, dst_path, ovwrite=False, verbose=True):
    info = print if verbose else silence

    base_dir = dst_path
    if not os.path.isdir(base_dir):
        os.makedirs(base_dir)

    #assumes file is output of extract_profiles
    profiles = common.load_json(src_path)
    profiles = [p['profile'] for p in profiles if p['status'] == 'success']

    for i, profile in enumerate(profiles):
        info('in profile {}/{} (user "{}")'.format(
            i+1, len(profiles), profile['username']))
        dst_path = get_dst_avatar_path(profile, base_dir)
        if os.path.isfile(dst_path) and not ovwrite:
            info('\tavatar already exists, skipping')
            continue
        info('\tdownloading "{}" to "{}"...'.format(
            profile['avatar_url'], dst_path), flush=True, end=' ')
        download(profile['avatar_url'], dst_path)
        info('done')

    info('all done')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src_path',
        required=True,
        help='path to profiles JSON file',
    )
    parser.add_argument(
        '--dst_path',
        help='path to dir to save ({})'.format(DEF_DST_DIR_PATH),
        default=DEF_DST_DIR_PATH,
    )
    parser.add_argument(
        '--ovwrite',
        help='overwrite file if exists',
        default=False,
    )
    args = parser.parse_args()

    download_avatars(
        src_path=args.src_path,
        dst_path=args.dst_path,
        ovwrite=args.ovwrite,
    )


if __name__ == '__main__':
    main()
