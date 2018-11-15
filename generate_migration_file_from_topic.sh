#/bin/bash

url=$1
[[ -z $url ]] && { echo 'must provide topic url'; exit 1; }
shift

set -ex

(cd ./crawl && ./crawl_topic.sh $url)
(cd ./gen_db_data \
    && ./gen_data_for_db_from_profiles.py --src_path ../crawl/profiles.json\
    --dst_path $(pwd)/migration-data.json)
