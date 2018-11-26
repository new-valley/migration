#!/usr/bin/env python3


import json
import argparse
import os
import user as u


DEF_DST_PATH = './messages.json'
FORUM_LINK = 'http://newvalley.xyz'


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)


def load_json(path):
    with open(path) as f:
        data = json.load(f)
    return data


def mk_message_body(username, password, email):
    lines = [
        'olar {}!'.format(username),
        'sou da equipe de desenvolvimento do novo fórum New Valley',
        'criamos uma conta para você no novo fórum com esse seu username.',
        '',
        'pra fazer login:',
        '- entre em {}'.format(FORUM_LINK),
        '- no menu no canto superior direito, clique em "ENTRAR" '
            'e use as credenciais:',
        '-- email: {}'.format(email),
        '-- senha: {}'.format(password),
        '',
        'voce vai poder (e deve) mudar seu email e senha quando entrar.',
        'ABRAÇOS',
    ]
    return '\n'.join(lines)


def mk_message(username, password, email):
    return {
        'recipient': username,
        'subject': '[NEW VALLEY] SUA CONTA NO NOVO FÓRUM',
        'message': mk_message_body(username, password, email),
    }


def mk_messages(src_path, dst_path):
    #assumes its JSON output of gen_data_for_db_from_profiles
    users = load_json(src_path)['users']

    msgs = []
    for user in users:
        msg = mk_message(user['username'], user['password'], user['email'])
        msgs.append(msg)

    save_json(dst_path, msgs)
    print('saved messages to "{}"'.format(dst_path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--src_path',
        required=True,
        help='path to JSON file with user data generated for DB',
    )
    parser.add_argument(
        '--dst_path',
        nargs='?',
        help='path to save messages .json file ({})'.format(DEF_DST_PATH),
        default=DEF_DST_PATH,
    )
    args = parser.parse_args()

    mk_messages(
        src_path=args.src_path,
        dst_path=args.dst_path,
    )


if __name__ == '__main__':
    main()
