#!/bin/bash

url=$1
[[ -z $url ]] && { echo 'must provide topic url'; exit 1; }
shift

set -ex

./extract_topic_profile_links.py \
    --url "$url" --dst_path 'links.json' $@
./extract_profiles.py \
    --src_path 'links.json' --dst_path 'profiles.json' $@
